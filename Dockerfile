FROM python:3
ENV PYTHONUNBUFFERED=1
WORKDIR /Alumni_Portal
COPY requirements.txt /Alumni_Portal/
RUN pip install -r requirements.txt
COPY . /Alumni_Portal
