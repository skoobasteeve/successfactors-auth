FROM public.ecr.aws/lambda/python:3.9

# Install the function's dependencies using file requirements.txt
# from your project folder.
RUN yum install -y \
gcc \
gcc-c++ \
Cython \
make \
libxml2 \
libxslt \
xmlsec1 \
xmlsec1-devel \
xmlsec1-openssl \
libtool-ltdl-devel

COPY requirements.txt  .
RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Copy function code
COPY lambda_function/* ${LAMBDA_TASK_ROOT}/

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "lambda_function.lambda_handler" ] 