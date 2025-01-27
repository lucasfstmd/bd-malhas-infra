FROM python:3.12.4-bullseye as spark-base

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      sudo \
      curl \
      vim \
      unzip \
      rsync \
      openjdk-11-jdk \
      build-essential \
      software-properties-common \
      ssh && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


## Download spark and hadoop dependencies and install

# Optional env variables
ENV SPARK_HOME=${SPARK_HOME:-"/opt/spark"}
ENV HADOOP_HOME=${HADOOP_HOME:-"/opt/hadoop"}

RUN mkdir -p ${HADOOP_HOME} && mkdir -p ${SPARK_HOME}
WORKDIR ${SPARK_HOME}


RUN curl https://ftp.unicamp.br/pub/apache/spark/spark-3.3.1/spark-3.3.1-bin-hadoop3.tgz -o spark-3.3.1-bin-hadoop3.tgz \
 && tar xvzf spark-3.3.1-bin-hadoop3.tgz --directory /opt/spark --strip-components 1 \
 && rm -rf spark-3.3.1-bin-hadoop3.tgz


FROM spark-base as pyspark

# Install python deps
COPY requirements.txt .
RUN pip3 install -r requirements.txt
RUN cd /opt && curl "https://drive.usercontent.google.com/download?id=1mUw5bCg2DI8G8VZDSfGbiw7d-l67dMm_&confirm=yy" -o IBM.tar.gz

ENV PATH="/opt/spark/sbin:/opt/spark/bin:${PATH}"
ENV SPARK_HOME="/opt/spark"
ENV SPARK_MASTER="spark://spark-master:7077"
ENV SPARK_MASTER_HOST spark-master
ENV SPARK_MASTER_PORT 7077
ENV PYSPARK_PYTHON python3
# Prepare env for install CSDK
ENV INFORMIXDIR=/opt/IBM/Informix_Client-SDK
ENV CSDK_HOME=$INFORMIXDIR
ENV LIBPATH=$INFORMIXDIR/lib:$INFORMIXDIR/lib/cli:$INFORMIXDIR/lib/esql:$INFORMIXDIR/lib:$INFORMIXDIR/bin:$INFORMIXDIR/etc:$LIBPATH
ENV ODBCSYSINI=$INFORMIXDIR/etc
ENV ODBCINI=$INFORMIXDIR/etc/odbc.ini
ENV LD_LIBRARY_PATH=$INFORMIXDIR/lib:$INFORMIXDIR/lib/esql:$INFORMIXDIR/lib/tools:$INFORMIXDIR/lib/cli
ENV INFORMIXSQLHOSTS=$INFORMIXDIR/etc/sqlhosts
ENV PATH=$INFORMIXDIR/bin:$PATH

COPY spark-defaults.conf "$SPARK_HOME/conf"

RUN chmod u+x /opt/spark/sbin/* && \
    chmod u+x /opt/spark/bin/* && \
    cd /opt && tar -xzvf IBM.tar.gz

ENV PYTHONPATH=$SPARK_HOME/python/:$PYTHONPATH

COPY entrypoint.sh .
RUN chmod 777 ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]