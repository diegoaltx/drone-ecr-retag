FROM python:3-alpine
WORKDIR /usr/src/drone-plugin
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENTRYPOINT [ "python", "/usr/src/drone-plugin/ecr-retag.py" ]
