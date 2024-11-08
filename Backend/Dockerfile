FROM public.ecr.aws/lambda/python:3.9

# Install system dependencies
RUN yum update -y && \
    yum install -y \
    gcc \
    python3-devel \
    graphviz \
    graphviz-devel \
    libglvnd-glx \
    make \
    && yum clean all

# Set the working directory
WORKDIR ${LAMBDA_TASK_ROOT}

# Create and set permissions for temp directory
RUN mkdir -p /tmp && \
    chmod 777 /tmp

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Verify Graphviz installation and permissions
RUN python -c "import graphviz; print('Graphviz version:', graphviz.__version__)" && \
    dot -V && \
    python -c "import os; os.makedirs('/tmp/test', exist_ok=True); assert os.access('/tmp/test', os.W_OK), '/tmp is not writable'"

# Copy necessary files
COPY local_index/ ./local_index/
COPY diag_mapping.json .
COPY claude3_tools.py .
COPY lambda_function.py .

# Set environment variables
ENV TEMP_DIR="/tmp"
ENV DIAGRAMS_OUTPUT_DIR=/tmp
ENV PYTHONPATH=${LAMBDA_TASK_ROOT}
ENV PATH="/usr/local/bin:${PATH}"

# Set the CMD to your handler
CMD [ "lambda_function.handler" ]