# Using Ubuntu 18.04
FROM ubuntu:18.04

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies for Ubuntu 18.04
RUN apt-get update && apt-get install -y \
  cmake \
  coinor-libclp-dev \
  coinor-libcoinutils-dev \
  coinor-libosi-dev \
  coinor-libcbc-dev \
  coinor-libcgl-dev \
  zlib1g-dev \
  libbz2-dev \
  doxygen \
  bison \
  flex \
  git \
  g++ \
  make \
  ca-certificates \
  dos2unix \
  && rm -rf /var/lib/apt/lists/*

# Define the working directory
WORKDIR /opt/popf-tif

# Clone the repository and compile the code
RUN git clone https://github.com/popftif/popf-tif . && \
  cd planner/src && \
  chmod +x ./build-instructions.txt && \
  ./build-instructions.txt && \
  cd ../release && \
  make popf3-clp

# Copy the entry point script to the container
COPY entrypoint.sh /usr/local/bin/entrypoint.sh

# Enable execute permissions for the entry point script
RUN dos2unix /usr/local/bin/entrypoint.sh && \
  chmod +x /usr/local/bin/entrypoint.sh && \
  ln -sf $(find /opt/popf-tif/planner/release -name "popf3-clp" | head -n 1) /usr/local/bin/popf3-clp && \
  chmod +x /usr/local/bin/popf3-clp

RUN mkdir /output && chmod 777 /output

# Directory for PDDL files
WORKDIR /data

# Set the entry point to the compiled binary
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]