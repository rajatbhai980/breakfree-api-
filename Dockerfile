#build stage 
FROM python:3.13-slim AS builder

# Create the app directory
RUN mkdir /breakfree-api
 
# Set the working directory inside the container
WORKDIR /breakfree-api
 
# Set environment variables 
# Prevents Python from writing pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
#Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1 
 
# Upgrade pip
RUN pip install --upgrade pip 
 
# Copy the Django project  and install dependencies
COPY requirements.txt  /breakfree-api/
 
# run this command to install all dependencies 
RUN pip install --no-cache-dir -r requirements.txt

#produtction stage 
FROM python:3.13-slim

 #switch to system user 
RUN useradd -m -r appuser && \
    mkdir /breakfree-api && \
    chown -R appuser /breakfree-api

# Copy the Python dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

#change working directory 
WORKDIR /breakfree-api

# Copy application code change owner 
COPY --chown=appuser:appuser . .

# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 

RUN chmod +x /breakfree-api/entrypoint.prod.sh 

#switch user 
USER appuser 
 
# Expose the Django port
EXPOSE 8000

ENTRYPOINT ["/breakfree-api/entrypoint.prod.sh"]