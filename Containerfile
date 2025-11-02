FROM registry.access.redhat.com/ubi9/python-311:latest

WORKDIR /opt/app
COPY . /opt/app

# Make top-level packages importable (agents/)
ENV PYTHONPATH=/opt/app

# Install deps (adjust if your requirements.txt is at repo root)
RUN pip install --no-cache-dir -r app/requirements.txt gunicorn

# No chmod/chgrp here (rootless-safe)

EXPOSE 8080
ENV HOST=0.0.0.0 PORT=8080 TODOS_FILE=/tmp/todos.json
CMD ["gunicorn","-w","2","--threads","4","-b","0.0.0.0:8080","app.app:app"]

