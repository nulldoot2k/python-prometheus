FROM python:3

RUN useradd -m myuser -u 1000

WORKDIR /app

COPY app.py .
COPY requirement.txt .
COPY templates templates/
RUN pip install --no-cache-dir -r requirement.txt

RUN chown -R myuser:myuser /app
USER myuser

EXPOSE 8080
EXPOSE 9090

CMD ["python", "app.py"]
