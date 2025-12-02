FROM python:3.13-slim

WORKDIR /app

#the image must install all
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#copy source files
COPY . .

#expose port 500
EXPOSE 5000

#run the Flask Server
CMD ["python","app.py"]
