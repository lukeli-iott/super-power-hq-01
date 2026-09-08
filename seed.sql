-- Super Powers HQ — existing submissions
-- Loaded into heroes.db so you have data to work with from step 1.

INSERT INTO submissions (hero_name, powers, age, location, email) VALUES
  ('Captain Comet', 'Flight, Super Speed',            '34', 'London',     'comet@sphq.example'),
  ('Mind Maven',    'Telepathy',                       '29', 'Manchester', 'maven@sphq.example'),
  ('Aqua Surge',    'Hydrokinesis',                    '41', 'Brighton',   'surge@sphq.example'),
  ('Ember',         'Pyrokinesis',                     '26', 'London',     'ember@sphq.example'),
  ('Stonewall',     'Super Strength, Invulnerability', '38', 'Birmingham', 'stonewall@sphq.example'),
  ('Whisper',       'Invisibility, Stealth',           '31', 'Manchester', 'whisper@sphq.example'),
  ('Voltaic',       'Electrokinesis',                  '23', 'Glasgow',    'voltaic@sphq.example'),
  ('Terra Nova',    'Geokinesis',                      '45', 'Cardiff',    'terranova@sphq.example');

-- A few more recent arrivals from HQ intake.
INSERT INTO submissions (hero_name, powers, age, location, email) VALUES
  ('Captain Comet', 'Flight, Super Speed',             '34', 'London',  'comet@sphq.example'),
  ('Glitch',        'Invisibility',                    'unknown', 'Leeds',  'not-an-email'),
  ('Nameless Null', NULL,                              '500', 'Bristol', 'null@sphq.example');
