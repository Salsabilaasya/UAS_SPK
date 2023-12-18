delete from tbl_restoran_online;

INSERT INTO tbl_restoran_online (no, nama_restoran, harga, rating_restoran, pelayanan, jarak, estimasi_waktu_pengantaran)
VALUES
  ('1', 'KFC', '46000', '4.6', '60', '7.5', '35 menit'),
  ('2', 'McDonald', '65000', '4.8', '90', '7.9', '30 menit'),
  ('3', 'Burger King', '37000', '4.7', '75', '7.2', '40 menit'),
  ('4', 'Richeese Factory', '45000', '4.7', '60', '9.8', '45 menit'),
  ('5', 'HokBen', '38000', '4.8', '90', '8.7', '40 menit'),
  ('6', 'Pizza Hut', '78000', '4.8', '70', '8.5', '45 menit'),
  ('7', 'J.CO Donuts & Coffee', '93000', '4.8', '60', '7.2', '40 menit'),
  ('8', 'Subway', '45000', '4.7', '65', '19.2', '55 menit'),
  ('9', 'Domino Pizza', '68000', '4.8', '68', '9.6', '38 menit'),
  ('10', 'A&W', '30000', '4.8', '75', '13.2', '45 menit');
  
  select*from tbl_restoran_online;