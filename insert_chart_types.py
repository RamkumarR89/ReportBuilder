from app.core.database import SessionLocal
from app.models.models import ChartType

chart_types = [
    {"Name": "Line", "Description": "Line Chart"},
    {"Name": "Bar", "Description": "Bar Chart"},
    {"Name": "Pie", "Description": "Pie Chart"},
    {"Name": "Scatter", "Description": "Scatter Chart"},
    {"Name": "Area", "Description": "Area Chart"},
    {"Name": "Column", "Description": "Column Chart"},
    {"Name": "Bubble", "Description": "Bubble Chart"},
    {"Name": "Radar", "Description": "Radar Chart"},
    {"Name": "HeatMap", "Description": "HeatMap Chart"},
    {"Name": "BoxPlot", "Description": "BoxPlot Chart"},
    {"Name": "Funnel", "Description": "Funnel Chart"},
    {"Name": "Gauge", "Description": "Gauge Chart"},
    {"Name": "Waterfall", "Description": "Waterfall Chart"},
    {"Name": "Candlestick", "Description": "Candlestick Chart"},
    {"Name": "TreeMap", "Description": "TreeMap Chart"},
]

db = SessionLocal()
for ct in chart_types:
    exists = db.query(ChartType).filter_by(Name=ct["Name"]).first()
    if not exists:
        db.add(ChartType(Name=ct["Name"], Description=ct["Description"]))
db.commit()
db.close()
print("Inserted chart types.") 