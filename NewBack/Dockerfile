FROM public.ecr.aws/lambda/python:3.9

# Install system dependencies
RUN yum update -y && \
    yum install -y \
        gcc \
        python3-devel \
        graphviz \
        graphviz-devel \
        make \
    && yum clean all \
    && rm -rf /var/cache/yum

# Set up directories and permissions
WORKDIR ${LAMBDA_TASK_ROOT}
RUN mkdir -p /tmp && \
    chmod 777 /tmp && \
    chmod 777 ${LAMBDA_TASK_ROOT}

# Create directories for Graphviz
RUN mkdir -p /opt/graphviz/bin && \
    mkdir -p /opt/graphviz/lib && \
    cp /usr/bin/dot /opt/graphviz/bin/ && \
    cp -r /usr/lib64/graphviz* /opt/graphviz/lib/ && \
    chmod -R 755 /opt/graphviz

# Test graphviz installation
RUN dot -V

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Verify diagrams installation
RUN python -c "import diagrams" || pip install --no-cache-dir diagrams && \
    python -c "import diagrams" && \
    echo "Diagrams package verified"

# Copy application files
COPY local_index/ ./local_index/
COPY diag_mapping.json .
COPY claude3_tools.py .
COPY lambda_function.py .

# Set environment variables
ENV DIAGRAMS_OUTPUT_DIR=/tmp \
    PYTHONPATH=${LAMBDA_TASK_ROOT} \
    PATH="/usr/local/bin:/opt/graphviz/bin:${PATH}" \
    LD_LIBRARY_PATH="/opt/graphviz/lib:${LD_LIBRARY_PATH}" \
    DIAGRAM_BUCKET_NAME=amazonqbucketsmile \
    PYTHONUNBUFFERED=1

# Verify the final setup
RUN python -c "from diagrams import Diagram; print('Diagram import successful')" && \
    dot -V && \
    echo "Final verification complete"

# Set the CMD to your handler
CMD [ "lambda_function.handler" ]