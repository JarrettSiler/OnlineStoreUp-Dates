# Use an official Python runtime as a parent image
FROM python:3.9
WORKDIR /project
COPY . .
EXPOSE 80
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "app/your_app_script.py"]