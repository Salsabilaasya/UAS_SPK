from sqlalchemy import String, Integer, Column
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Restoran(Base):
    __tablename__ = "tbl_restoran_online"
    no = Column(Integer, primary_key=True)
    nama_restoran = Column(String)
    harga = Column(Integer)
    rating_restoran = Column(Integer)
    pelayanan = Column(Integer)
    jarak = Column(Integer)
    estimasi_waktu_pengantaran = Column(Integer)

    def __repr__(self):
        return f"Restoran(no={self.no!r}, nama_restoran={self.nama_restoran!r}, harga={self.harga!r}, rating_restoran={self.rating_restoran!r}, pelayanan={self.pelayanan!r}, jarak={self.jarak!r}, estimasi_waktu_pengantaran={self.estimasi_waktu_pengantaran!r})"