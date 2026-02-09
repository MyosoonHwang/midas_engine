from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class SearchLog(db.Model):
    __tablename__ = 'search_logs'
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(100), nullable=False)
    mode = db.Column(db.String(10), nullable=False)
    category = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.now)

class PriceRecord(db.Model):
    __tablename__ = 'price_records'
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(100), index=True)
    category = db.Column(db.String(20))
    naver_price = db.Column(db.BigInteger, default=0)
    bungae_price = db.Column(db.BigInteger, default=0)
    ai_estimated_price = db.Column(db.BigInteger, default=0)
    ai_score = db.Column(db.Integer, default=0)
    ai_reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)