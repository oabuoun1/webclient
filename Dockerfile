FROM python:3
RUN pip3 install netifaces
ADD webclient.py /
ENV SERVER 127.0.0.1
ENV PORT 8777
CMD [ "sh", "-c",  "python ./webclient.py --server ${SERVER} --port ${PORT}" ]