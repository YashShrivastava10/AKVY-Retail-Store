FROM python:3
    
ADD akvy_store.py .

RUN pip install geopy

RUN pip install dnspython3

RUN pip install numpy

RUN pip install pandas

RUN pip install pdfkit

RUN pip install pymongo

RUN pip install pytz

RUN pip install regex

RUN pip install tabulate

RUN pip install yagmail 

CMD ["python","./akvy_store.py"]