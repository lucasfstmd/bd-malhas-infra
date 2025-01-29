# Baseado na imagem oficial do Airflow
FROM apache/airflow:2.10.4

# Instalar dependências adicionais, incluindo o bash e Java
USER root
RUN apt-get update && apt-get install -y bash openjdk-17-jdk && rm -rf /var/lib/apt/lists/*

# Definir JAVA_HOME e atualizar PATH
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

# Install python deps
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Config and install ODBC 17 for sql server
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17

RUN chmod 644 /etc/odbcinst.ini && \
    echo "[ODBC Driver 17 for SQL Server]" > /etc/odbcinst.ini && \
    echo "Description=ODBC Driver 17 for SQL Server" >> /etc/odbcinst.ini && \
    echo "Driver=/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.10.so.6.1" >> /etc/odbcinst.ini

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
