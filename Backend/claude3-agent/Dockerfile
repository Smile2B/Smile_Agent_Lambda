FROM public.ecr.aws/lambda/python:3.9

# Install system dependencies
RUN yum update -y && \
    yum install -y \
    gcc \
    python3-devel \
    graphviz \
    graphviz-devel \
    make \
    && yum clean all

# Set the working directory
WORKDIR ${LAMBDA_TASK_ROOT}

# Ensure /tmp exists and has correct permissions
RUN mkdir -p /tmp && \
    chmod 777 /tmp

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy necessary files
COPY local_index/ ./local_index/
COPY diag_mapping.json .
COPY claude3_tools.py .
COPY lambda_function.py .

# Set environment variable for diagrams library
ENV DIAGRAMS_OUTPUT_DIR=/tmp

# Set the CMD to your handler
CMD [ "lambda_function.handler" ]