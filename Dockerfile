FROM python:3
ADD webclient.py /
ENTRYPOINT ["python3", "./webclient.py"]
CMD []