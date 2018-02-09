FROM ubuntu:16.04

# https://github.com/docker/docker/blob/9a9fc01af8fb5d98b8eec0740716226fadb3735c/contrib/mkimage/debootstrap
RUN set -xe \
  \
  && echo '#!/bin/sh' > /usr/sbin/policy-rc.d \
  && echo 'exit 101' >> /usr/sbin/policy-rc.d \
  && chmod +x /usr/sbin/policy-rc.d \
  \
  && dpkg-divert --local --rename --add /sbin/initctl \
  && cp -a /usr/sbin/policy-rc.d /sbin/initctl \
  && sed -i 's/^exit.*/exit 0/' /sbin/initctl \
  \
  && echo 'force-unsafe-io' > /etc/dpkg/dpkg.cfg.d/docker-apt-speedup \
  \
  && echo 'DPkg::Post-Invoke { "rm -f /var/cache/apt/archives/*.deb /var/cache/apt/archives/partial/*.deb /var/cache/apt/*.bin || true"; };' > /etc/apt/apt.conf.d/docker-clean \
  && echo 'APT::Update::Post-Invoke { "rm -f /var/cache/apt/archives/*.deb /var/cache/apt/archives/partial/*.deb /var/cache/apt/*.bin || true"; };' >> /etc/apt/apt.conf.d/docker-clean \
  && echo 'Dir::Cache::pkgcache ""; Dir::Cache::srcpkgcache "";' >> /etc/apt/apt.conf.d/docker-clean \
  \
  && echo 'Acquire::Languages "none";' > /etc/apt/apt.conf.d/docker-no-languages \
  \
  && echo 'Acquire::GzipIndexes "true"; Acquire::CompressionTypes::Order:: "gz";' > /etc/apt/apt.conf.d/docker-gzip-indexes \
  \
  && echo 'Apt::AutoRemove::SuggestsImportant "false";' > /etc/apt/apt.conf.d/docker-autoremove-suggests

# delete all the apt list files since they're big and get stale quickly
RUN rm -rf /var/lib/apt/lists/*
# this forces "apt-get update" in dependent images, which is also good

# enable the universe
RUN sed -i 's/^#\s*\(deb.*universe\)$/\1/g' /etc/apt/sources.list

# make systemd-detect-virt return "docker"
# See: https://github.com/systemd/systemd/blob/aa0c34279ee40bce2f9681b496922dedbadfca19/src/basic/virt.c#L434
RUN mkdir -p /run/systemd && echo 'docker' > /run/systemd/container


# Install apt
RUN set -ex \
  && buildDeps=' \
    automake \
    autotools-dev \
    autoconf \
    libtool \
    build-essential \
    ca-certificates \
    gcc \
    make \
    pkg-config \
    bzip2 \
    libbz2-dev \
    libpq-dev \
    wget \
    curl \
    apt-transport-https \
    tcl \
    tk \
    dpkg-dev \
    tcl-dev \
    tk-dev \
    g++ \
    xz-utils \
    file \
    zlib1g-dev \
    locales \
    cmake \
    lsb-release \
    jq \
    git \
    nano \
    nkf \
    zsh \
    tmux \
    htop \
    parallel \
  ' \
  && apt-get update && apt-get install -y $buildDeps --no-install-recommends

# Install miniconda to /miniconda
ENV PATH /miniconda/bin:${PATH}
RUN curl -LO http://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh \
  && bash Miniconda-latest-Linux-x86_64.sh -p /miniconda -b \
  && rm Miniconda-latest-Linux-x86_64.sh \
  && conda update -y conda && pip install -U pip

RUN conda create -n py2 python=2.7 && /bin/bash -c "source activate py2 && pip install -U pip"
RUN conda create -n py3 python=3.6 && /bin/bash -c "source activate py3 && pip install -U pip"
ENV PATH /miniconda/envs/py3/bin:$PATH

# Install Google Cloud SDK
ENV CLOUDSDK_PYTHON /miniconda/envs/py2/bin/python
RUN echo "deb https://packages.cloud.google.com/apt cloud-sdk-$(lsb_release -c -s) main" >> /etc/apt/sources.list.d/google-cloud-sdk.list \
  && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - \
  && apt-get update && apt-get install google-cloud-sdk -y --no-install-recommends
## Init
COPY key.json /key.json
RUN gcloud auth activate-service-account --key-file=/key.json
ENV GOOGLE_APPLICATION_CREDENTIALS /key.json


# MeCab
RUN git clone https://github.com/taku910/mecab.git \
  && cd mecab/mecab \
  && ./configure --enable-utf8-only --with-charset=utf8 \
  && make -j4 && make install \
  && cd .. && ldconfig \
  # Install IPA dict
  && cd mecab-ipadic \
  && ./configure --with-charset=utf8 \
  && make -j4 && make install \
  && cd ../.. && rm -fr mecab
#   # Install Neologd
# RUN git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git \
#   && mecab-ipadic-neologd/bin/install-mecab-ipadic-neologd -n -y \
#   && cd mecab-ipadic-neologd \
#   && neologd_date=$(git log --pretty=format:'{%n  "commit": "%H",%n  "author": "%aN <%aE>",%n  "date": "%ad",%n  "message": "%f"%n},' $@ | perl -pe 'BEGIN{print "["}; END{print "]\n"}' | perl -pe 's/},]/}]/'|jq '.[]'|jq .date|sed 's/"[A-Za-z]* \([A-Za-z]*\) \([0-9]*\) [^ ]* \([0-9]*\) .*/\1-\2-\3/'|xargs date "+%Y%m%d" -d) \
#   && echo "NEOLOGD_VERSION=${neologd_date}"  > /NEOLOGD_VERSION \
#   && cd .. && rm -rf mecab-ipadic-neologd \
#   && sed -i -e"s/^dicdir =  \/usr\/local\/lib\/mecab\/dic\/ipadic/dicdir =  \/usr\/local\/lib\/mecab\/dic\/mecab-ipadic-neologd/" /usr/local/etc/mecabrc


# Juman
RUN wget -O juman-7.01.tar.bz2 http://nlp.ist.i.kyoto-u.ac.jp/nl-resource/juman/juman-7.01.tar.bz2 \
  && tar jxvf juman-7.01.tar.bz2 && cd juman-7.01 \
  && ./configure && make -j4 && make install \
  && cd .. && rm -fr juman-7.01*

# Juman++v2
RUN wget -O jumanpp-2.0.0-rc1.tar.xz https://github.com/ku-nlp/jumanpp/releases/download/v2.0.0-rc1/jumanpp-2.0.0-rc1.tar.xz \
  && tar xf jumanpp-2.0.0-rc1.tar.xz && cd jumanpp-2.0.0-rc1 \
  && mkdir bld && cd bld \
  && cmake .. -DCMAKE_BUILD_TYPE=Release && make install -j4 \
  && cd ../.. && rm -fr jumanpp-2.0.0-rc1*

# KNP
# v4.18 has case analysis bug; use fixed version.
# wget -O knp-4.18.tar.bz2 http://nlp.ist.i.kyoto-u.ac.jp/nl-resource/knp/knp-4.18.tar.bz2
# wget -O knp-4.18.tar.bz2 http://nlp.ist.i.kyoto-u.ac.jp/nl-resource/knp/knp-4.18.tar.bz2 \
RUN bucket=nd-tools && target=knp-4.18.tar.gz && gsutil -o GSUtil:parallel_composite_upload_threshold=128M cp gs://${bucket}/${target} ./${target}
RUN tar zxf knp-4.18.tar.gz
RUN cd knp-4.18 \
  && autoreconf --install \
  && ./configure \
  && make -j4 && make install \
  && cd .. && rm -fr knp-4.18*

# PyKNP
RUN git clone https://github.com/kzinmr/pyknp-extend.git \
  && cd pyknp-extend \
  && python setup.py install

# Use Japanese locale
RUN locale-gen ja_JP.UTF-8
ENV LANG ja_JP.UTF-8
ENV LC_CTYPE ja_JP.UTF-8
RUN localedef -f UTF-8 -i ja_JP ja_JP.utf8

RUN /bin/bash -c "source activate py3 && pip install --no-cache mojimoji==0.0.6 nltk==3.2.5"
RUN /bin/bash -c "source activate py3 && conda install jupyterlab numpy -c defaults"

CMD ["/bin/bash"]