# Base image that bundles AWS Lambda Python 3.8 image with some middleware functions
FROM ghcr.io/lambda-feedback/baseevalutionfunctionlayer:main-3.8

WORKDIR /app

RUN yum install -y git

# Copy and install any packages/modules needed for your evaluation script.
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy the evaluation and testing scripts
COPY evaluation.py ./app/
COPY evaluation_tests.py ./app/
COPY expression_utilities.py ./app/
COPY buckingham_pi_utilities.py ./app/

# Copy the preview and testing scripts
COPY preview.py ./app/
COPY preview_tests.py ./app/

# Copy Documentation
COPY docs/dev.md ./app/docs/dev.md
COPY docs/user.md ./app/docs/user.md

# Set permissions so files and directories can be accessed on AWS
RUN chmod 644 $(find . -type f)
RUN chmod 755 $(find . -type d)

# The entrypoint for AWS is to invoke the handler function within the app package
CMD [ "/app/app.handler" ]
