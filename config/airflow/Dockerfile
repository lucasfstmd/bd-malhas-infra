# Baseado na imagem oficial do Airflow
FROM apache/airflow:2.10.4

# Instalar dependências adicionais, incluindo o bash
USER root
RUN apt-get update && apt-get install -y bash && rm -rf /var/lib/apt/lists/*

# Provide CSDK Files
RUN cd /opt && curl "https://drive.usercontent.google.com/download?id=1mUw5bCg2DI8G8VZDSfGbiw7d-l67dMm_&confirm=yy" -o IBM.tar.gz

# Prepare env for install CSDK
ENV INFORMIXDIR=/opt/IBM/Informix_Client-SDK
ENV CSDK_HOME=$INFORMIXDIR
ENV LIBPATH=$INFORMIXDIR/lib:$INFORMIXDIR/lib/cli:$INFORMIXDIR/lib/esql:$INFORMIXDIR/lib:$INFORMIXDIR/bin:$INFORMIXDIR/etc:$LIBPATH
ENV ODBCSYSINI=$INFORMIXDIR/etc
ENV ODBCINI=$INFORMIXDIR/etc/odbc.ini
ENV LD_LIBRARY_PATH=$INFORMIXDIR/lib:$INFORMIXDIR/lib/esql:$INFORMIXDIR/lib/tools:$INFORMIXDIR/lib/cli
ENV INFORMIXSQLHOSTS=$INFORMIXDIR/etc/sqlhosts
ENV PATH=$INFORMIXDIR/bin:$PATH

# Install CSDK
RUN cd /opt && tar -xzvf IBM.tar.gz

# Retorne para o usuário padrão
USER airflow
