from app.core.database import SessionLocal
from app.models.models import ChartType
from datetime import datetime

chart_types = [
    (1, 'Line', 'Line Chart - Shows trends over time'),
    (2, 'Bar', 'Bar Chart - Compares values across categories'),
    (3, 'Pie', 'Pie Chart - Shows proportions of a whole'),
    (4, 'Scatter', 'Scatter Plot - Shows relationships between variables'),
    (5, 'Area', 'Area Chart - Shows cumulative values over time'),
    (6, 'Column', 'Column Chart - Vertical bar chart'),
    (7, 'Bubble', 'Bubble Chart - Shows three dimensions of data'),
    (8, 'Radar', 'Radar Chart - Shows multiple variables'),
    (9, 'HeatMap', 'Heat Map - Shows data density'),
    (10, 'BoxPlot', 'Box Plot - Shows statistical distributions'),
    (11, 'Funnel', 'Funnel Chart - Shows stages in a process'),
    (12, 'Gauge', 'Gauge Chart - Shows progress towards a goal'),
    (13, 'Waterfall', 'Waterfall Chart - Shows cumulative effect'),
    (14, 'Candlestick', 'Candlestick Chart - Shows price movements'),
    (15, 'TreeMap', 'Tree Map - Shows hierarchical data'),
]

db = SessionLocal()
for ct in chart_types:
    if not db.query(ChartType).filter_by(Id=ct[0]).first():
        db.add(ChartType(Id=ct[0], Name=ct[1], Description=ct[2], CreatedAt=datetime.utcnow(), IsActive=True))
db.commit()
db.close()
print("Inserted default chart types if not present.") 