DROP SCHEMA IF EXISTS AEROMILES CASCADE;


CREATE SCHEMA AEROMILES;


SET search_path to AEROMILES;


CREATE TABLE PENGGUNA (
    email           VARCHAR(100)   PRIMARY KEY,
    password        VARCHAR(255)    NOT NULL,
    salutation      VARCHAR(10)     NOT NULL      CHECK (salutation IN ('Mr.', 'Mrs.', 'Ms.', 'Dr.')),
    first_mid_name  VARCHAR(100)    NOT NULL,
    last_name       VARCHAR(100)    NOT NULL,
    country_code    VARCHAR(5)      NOT NULL,
    mobile_number   VARCHAR(20)     NOT NULL,
    tanggal_lahir   DATE            NOT NULL,
    kewarganegaraan VARCHAR(50)     NOT NULL
);


CREATE OR REPLACE FUNCTION check_available_email()
RETURNS TRIGGER AS
$$
BEGIN
    IF EXISTS (SELECT 1 FROM PENGGUNA WHERE lower(email) = lower(NEW.email)) THEN
        RAISE EXCEPTION 'ERROR: Email % sudah terdaftar, silakan gunakan email lain.', NEW.email;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE TRIGGER trg_check_available_email
BEFORE INSERT ON PENGGUNA
FOR EACH ROW 
EXECUTE FUNCTION check_available_email();


CREATE OR REPLACE FUNCTION fn_login_pengguna(
    p_email VARCHAR,
    p_password VARCHAR
) RETURNS TEXT
AS $$
DECLARE
    result TEXT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM PENGGUNA 
        WHERE lower(email) = lower(p_email) AND password = p_password
    ) THEN
        result := 'Email atau password salah, silakan coba lagi.';
    ELSE
        result := FORMAT('SUKSES: Login berhasil. Selamat datang, %s!', p_email);
    END IF;
    RETURN result;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION fungsi_update_tier_member()
RETURNS TRIGGER AS $$
DECLARE
    v_frekuensi_terbang INT;
    v_id_tier_baru VARCHAR(10);
    v_nama_tier_lama VARCHAR(50);
    v_nama_tier_baru VARCHAR(50);
BEGIN
    SELECT COUNT(*) INTO v_frekuensi_terbang
    FROM CLAIM_MISSING_MILES
    WHERE email_member = NEW.email AND status_penerimaan = 'Disetujui';
    SELECT id_tier INTO v_id_tier_baru
    FROM TIER
    WHERE minimal_tier_miles <= NEW.total_miles 
        OR minimal_frekuensi_terbang <= v_frekuensi_terbang
    ORDER BY minimal_tier_miles DESC
    LIMIT 1;

    IF v_id_tier_baru IS NOT NULL AND v_id_tier_baru <> OLD.id_tier THEN
        SELECT nama INTO v_nama_tier_lama 
        FROM TIER 
        WHERE id_tier = OLD.id_tier;
        
        SELECT nama INTO v_nama_tier_baru 
        FROM TIER 
        WHERE id_tier = v_id_tier_baru;

        NEW.id_tier := v_id_tier_baru;

        RAISE NOTICE 'SUKSES: Tier Member "%" telah diperbarui dari "%" menjadi "%" berdasarkan total miles yang dimiliki.', 
                    NEW.email, v_nama_tier_lama, v_nama_tier_baru;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


INSERT INTO PENGGUNA (email, password, salutation, first_mid_name, last_name, country_code, mobile_number, tanggal_lahir, kewarganegaraan) VALUES 
('strawberry.shortcake@gmail.com',    '$2b$12$KxQmN3vLpR4sT6uW8yZaAeBfCgDhEiGjHkIlJmKnLoMpNqOrPsQuRv', 'Ms.', 'Strawberry',       'Shortcake',  '+1',   '5551901615', '1990-06-15', 'American'),
('blueberry.muffin@gmail.com',        '$2b$12$LyRnO4wMqS5tU7vX9zAbBfCgDhEiGjHkIlJmKnLoMpNqOrPsQuRvSw', 'Ms.', 'Blueberry',         'Muffin',     '+1',   '5551912320', '1991-03-20', 'American'),
('orange.blossom@gmail.com',          '$2b$12$MzSoP5xNrT6uV8wY0aAcBdCeEfFgGhHiIjJkKlLmMnNoOpPqQrRsSt', 'Ms.', 'Orange',             'Blossom',    '+1',   '5551891005', '1989-10-05', 'American'),
('lemon.merringue@gmail.com',         '$2b$12$NaToQ6yOsU7vW9xZ1bBdCeCfDgEhFiGjHkIlJmKnLoMpNqOrPsQuRv', 'Ms.', 'Lemon',              'Merringue',  '+1',   '5551920722', '1992-07-22', 'American'),
('plum.pudding@gmail.com',            '$2b$12$ObUpR7zPtV8wX0yA2cCeBfDgEhFiGjHkIlJmKnLoMpNqOrPsQuRvSw', 'Mr.', 'Plum',               'Pudding',    '+1',   '5551881201', '1988-12-01', 'American'),
('cherry.jam@gmail.com',              '$2b$12$PcVqS8aQuW9xY1zA3dDfBgChDiEjFkGlHmInJoKpLqMrNsOtPuQvRw', 'Ms.', 'Cherry',             'Jam',        '+1',   '5551930430', '1993-04-30', 'American'),
('raspberry.torte@gmail.com',         '$2b$12$QdWrT9bRvX0yZ2aB4eEgChDiEjFkGlHmInJoKpLqMrNsOtPuQvRwSx', 'Ms.', 'Raspberry',          'Torte',      '+1',   '5551900914', '1990-09-14', 'American'),

('judy.hopps@yahoo.com',            '$2b$12$ReXsU0cSwY1zA3bC5fFhDiEjFkGlHmInJoKpLqMrNsOtPuQvRwSxTy', 'Ms.', 'Judy',               'Hopps',      '+1',   '5554941103', '1994-11-03', 'American'),
('nick.wilde@yahoo.com',            '$2b$12$SfYtV1dTxZ2aB4cD6gGiEjFkGlHmInJoKpLqMrNsOtPuQvRwSxTyUz', 'Mr.', 'Nick',               'Wilde',      '+1',   '5558560622', '1985-06-22', 'American'),
('fru.fru@yahoo.com',             '$2b$12$TgZuW2eUyA3bC5dE7hHjFkGlHmInJoKpLqMrNsOtPuQvRwSxTyUzVa', 'Ms.', 'Fru',                'Fru',        '+1',   '5559960214', '1996-02-14', 'American'),
('pawbert.linxley@yahoo.com',          '$2b$12$UhAvX3fVzB4cD6eF8iIkGlHmInJoKpLqMrNsOtPuQvRwSxTyUzVaBb', 'Mr.', 'Pawbert',            'Linxley',    '+1',   '5558050519', '1980-05-19', 'American'),

('choso.kamo@gmail.com',           '$2b$12$ViByY4gWaC5dE7fG9jJlHmInJoKpLqMrNsOtPuQvRwSxTyUzVaBbCc', 'Mr.', 'Choso',              'Kamo',       '+81',  '8031234001', '1981-01-07', 'Japanese'),
('hiromi.hiruguma@gmail.com',      '$2b$12$WjCzZ5hXbD6eF8gH0kKmInJoKpLqMrNsOtPuQvRwSxTyUzVaBbCcDd', 'Mr.', 'Hiromi',             'Hiruguma',   '+81',  '8031234002', '1999-08-15', 'Japanese'),
('yuji.itadori@gmail.com',         '$2b$12$XkDaA6iYcE7fG9hI1lLnJoKpLqMrNsOtPuQvRwSxTyUzVaBbCcDdEe', 'Mr.', 'Yuji',               'Itadori',    '+81',  '8031234003', '2000-03-20', 'Japanese'),
('megumi.fushiguro@gmail.com',     '$2b$12$YlEbB7jZdF8gH0iJ2mMoKpLqMrNsOtPuQvRwSxTyUzVaBbCcDdEeFf', 'Mr.', 'Megumi',             'Fushiguro',  '+81',  '8031234004', '2000-12-22', 'Japanese'),
('nobara.kugisaki@gmail.com',      '$2b$12$ZmFcC8kaEG9hI1jK3nNoLqMrNsOtPuQvRwSxTyUzVaBbCcDdEeFfGg', 'Ms.', 'Nobara',             'Kugisaki',   '+81',  '8031234005', '2001-08-07', 'Japanese'),
('satoru.gojo@gmail.com',          '$2b$12$AnGdD9lbFH0iJ2kL4ooOpMrNsOtPuQvRwSxTyUzVaBbCcDdEeFfGgHh', 'Mr.', 'Satoru',             'Gojo',       '+81',  '8031234006', '1989-12-07', 'Japanese'),
('suguru.geto@gmail.com',          '$2b$12$BoHeE0mcGI1jK3lM5ppPqNsOtPuQvRwSxTyUzVaBbCcDdEeFfGgHhIi', 'Mr.', 'Suguru',             'Geto',       '+81',  '8031234007', '1989-02-03', 'Japanese'),
('toji.fushiguro@gmail.com',       '$2b$12$CpIfF1ndHJ2kL4mN6qqRrOtPuQvRwSxTyUzVaBbCcDdEeFfGgHhIiJj', 'Mr.', 'Toji',               'Fushiguro',  '+81',  '8031234008', '1971-03-01', 'Japanese'),
('kento.nanami@gmail.com',         '$2b$12$DqJgG2oeIK3lM5nO7rrSsOuPvRwSxTyUzVaBbCcDdEeFfGgHhIiJjKk', 'Mr.', 'Kento',              'Nanami',     '+81',  '8031234009', '1985-06-28', 'Japanese'),
('shoko.ieiri@gmail.com',          '$2b$12$ErKhH3pfJL4mN6oP8ssTtPuQvRwSxTyUzVaBbCcDdEeFfGgHhIiJjKkLl', 'Dr.', 'Shoko',            'Ieiri',      '+81',  '8031234010', '1989-09-05', 'Japanese'),
('yuki.tsukumo@gmail.com',         '$2b$12$FsLiI4qgKM5nO7pQ9ttUuQvRwSxTyUzVaBbCcDdEeFfGgHhIiJjKkLlMm', 'Ms.', 'Yuki',            'Tsukumo',    '+81',  '8031234011', '1984-12-31', 'Japanese'),
('yuta.okkotsu@gmail.com',         '$2b$12$GtMjJ5rhLN6oP8qR0uuVvRwSxTyUzVaBbCcDdEeFfGgHhIiJjKkLlMmNn', 'Mr.', 'Yuta',            'Okkotsu',    '+81',  '8031234012', '2000-03-07', 'Japanese'),
('maki.zenin@gmail.com',           '$2b$12$HuNkK6siMO7pQ9rS1vvWwSxTyUzVaBbCcDdEeFfGgHhIiJjKkLlMmNnOo', 'Ms.', 'Maki',             'Zenin',      '+81',  '8031234013', '2001-01-20', 'Japanese'),

('twilight.sparkle@yahoo.com',        '$2b$12$IvOlL7tjNP8qR0sT2wwXxTyUzVaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPp', 'Ms.', 'Twilight',          'Sparkle',    '+1',   '5551951022', '1995-10-22', 'American'),
('pinkie.pie@yahoo.com',              '$2b$12$JwPmM8ukOQ9rS1tU3xxYyUzVaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQq', 'Ms.', 'Pinkie',             'Pie',        '+1',   '5551960503', '1996-05-03', 'American'),
('rainbow.dash@yahoo.com',            '$2b$12$KxQnN9vlPR0sT2uV4yyZzVaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRr', 'Ms.', 'Rainbow',            'Dash',       '+1',   '5551950401', '1995-04-01', 'American'),

('tony.stark@gmail.com',                 '$2b$12$LyRoO0wmQS1tU3vW5zzAaWbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSs', 'Mr.', 'Tony',              'Stark',      '+1',   '5557000529', '1970-05-29', 'American'),
('steve.rogers@gmail.com',               '$2b$12$MzSpP1xnRT2uV4wX6aaAbXcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTt', 'Mr.', 'Steve',              'Rogers',     '+1',   '5551180704', '1918-07-04', 'American'),
('bruce.banner@gmail.com',               '$2b$12$NaToQ2yoSU3vW5xY7bbBcYdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUu', 'Dr.', 'Bruce',              'Banner',     '+1',   '5556911218', '1969-12-18', 'American'),
('natasha.romanoff@gmail.com',           '$2b$12$ObUpR3zpTV4wX6yZ8ccCdZeEfFgGhHiIjJkKlLmMnNoOpPqQrRsSuTtUuVv', 'Ms.', 'Natasha',           'Romanoff',   '+7',   '9161234567', '1984-11-22', 'Russian'),
('peter.parker@gmail.com',               '$2b$12$PcVqS4aqUW5xY7zA9ddDeAfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuUvVw', 'Mr.', 'Peter',              'Parker',     '+1',   '5552010810', '2001-08-10', 'American'),
('wanda.maximoff@gmail.com',             '$2b$12$QdWrT5brVX6yZ8aB0eeEfBgGhHiIjJkKlLmMnNoOpPqQrRsStTuUvVwWx', 'Ms.', 'Wanda',              'Maximoff',   '+421', '9001234567', '1989-02-10', 'Sokovian'),
('scott.lang@gmail.com',                 '$2b$12$ReXsU6csWY7zA9bC1ffFgChHiIjJkKlLmMnNoOpPqQrRsStTuUvVwWxXx', 'Mr.', 'Scott',              'Lang',       '+1',   '5557240415', '1972-04-15', 'American'),

('will.byers@gmail.com',        '$2b$12$SfYtV7dtXZ8aB0cD2ggGhDiIjJkKlLmMnNoOpPqQrRsStTuUvVwWxXyYy', 'Mr.', 'Will',               'Byers',      '+1',   '5557110322', '1971-03-22', 'American'),
('jonathan.byers@gmail.com',    '$2b$12$TgZuW8euYA9bC1dE3hhHiEjJkKlLmMnNoOpPqQrRsStTuUvVwWxXyYzZz', 'Mr.', 'Jonathan',           'Byers',      '+1',   '5556671201', '1967-12-01', 'American'),
('mike.wheeler@gmail.com',      '$2b$12$UhAvX9fvZB0cD2eF4iiIjFkKlLmMnNoOpPqQrRsStTuUvVwWxXyYzZaAa', 'Mr.', 'Mike',               'Wheeler',    '+1',   '5557110407', '1971-04-07', 'American'),
('nancy.wheeler@gmail.com',     '$2b$12$ViByY0gwAC1dE3fG5jjJkGlLmMnNoOpPqQrRsStTuUvVwWxXyYzZaAbBb', 'Ms.', 'Nancy',              'Wheeler',    '+1',   '5556671114', '1967-11-14', 'American'),
('holly.wheeler@gmail.com',     '$2b$12$WjCzZ1hxBD2eF4gH6kkKlHmMnNoOpPqQrRsStTuUvVwWxXyYzZaAbBcCc', 'Ms.', 'Holly',              'Wheeler',    '+1',   '5558220719', '1982-07-19', 'American'),
('lucas.sinclair@gmail.com',    '$2b$12$XkDaA2iyC3fG5hI7llLmInNoOpPqQrRsStTuUvVwWxXyYzZaAbBcCdDd', 'Mr.', 'Lucas',              'Sinclair',   '+1',   '5557110601', '1971-06-01', 'American'),
('erica.sinclair@gmail.com',    '$2b$12$YlEbB3jzDEGH6iJ8mmMnJoOpPqQrRsStTuUvVwWxXyYzZaAbBcCdDeEe', 'Ms.', 'Erica',              'Sinclair',   '+1',   '5557750702', '1975-07-02', 'American'),
('dustin.henderson@gmail.com',  '$2b$12$ZmFcC4kaEF7gH9jK0nnNoKpPqQrRsStTuUvVwWxXyYzZaAbBcCdDeEfFf', 'Mr.', 'Dustin',             'Henderson',  '+1',   '5557110110', '1971-01-10', 'American'),
('steve.harrington@gmail.com',  '$2b$12$AnGdD5lbFG8hI0kL1ooOpLqRsStTuUvVwWxXyYzZaAbBcCdDeEfFgGg', 'Mr.', 'Steve',               'Harrington', '+1',   '5556660922', '1966-09-22', 'American'),
('max.mayfield@gmail.com',      '$2b$12$BoHeE6mcGH9iJ1lM2ppPqMrSsStTuUvVwWxXyYzZaAbBcCdDeEfFgGhHh', 'Ms.', 'Max',                'Mayfield',   '+1',   '5557110906', '1971-09-06', 'American'),
('jane.hopper@gmail.com',       '$2b$12$CpIfF7ndHI0jK2mN3qqQrNsTtUuVwWxXyYzZaAbBcCdDeEfFgGhHiIi', 'Ms.', 'Jane',                'Hopper',     '+1',   '5557111028', '1971-10-28', 'American'),

('larajean.songcovey@ui.ac.id',       '$2b$12$DqJgG8oeIJ1kL3nO4rrRoOtUuVwWxXyYzZaAbBcCdDeEfFgGhHiIjJj', 'Ms.', 'Lara Jean Song',    'Covey',      '+1',   '5551990420', '1999-04-20', 'American'),
('margot.songcovey@ui.ac.id',         '$2b$12$ErKhH9pfJK2lM4oP5ssSsPuVvWxXyYzZaAbBcCdDeEfFgGhHiIjJkKk', 'Ms.', 'Margot Song',       'Covey',      '+1',  '7911234567', '1997-08-12', 'American'),
('kitty.songcovey@ui.ac.id',          '$2b$12$FsLiI0qgKL3mN5pQ6ttTtQvWwXyYzZaAbBcCdDeEfFgGhHiIjJkKlLl', 'Ms.', 'Kitty Song',        'Covey',      '+1',   '5552030630', '2003-06-30', 'American'),
('peter.kavinsky@ui.ac.id',           '$2b$12$GtMjJ1rhLM4nO6qR7uuUuRwXxYzZaAbBcCdDeEfFgGhHiIjJkKlLmMm', 'Mr.', 'Peter',              'Kavinsky',   '+1',   '5551990622', '1999-06-22', 'American'),
('josh.sanderson@ui.ac.id',           '$2b$12$HuNkK2siMN5oP7rS8vvVvSxYyZaAbBcCdDeEfFgGhHiIjJkKlLmMnNn', 'Mr.', 'Josh',               'Sanderson',  '+1',   '5559940315', '1994-03-15', 'American'),

('isabel.conklin@yahoo.com',           '$2b$12$IvOlL3tjNO6pQ8sT9wwWwTyZzAaAbBcCdDeEfFgGhHiIjJkKlLmMnNoOo', 'Ms.', 'Isabel',            'Conklin',    '+1',   '5552000125', '2000-01-25', 'American'),
('steven.conklin@yahoo.com',           '$2b$12$JwPmM4ukOP7qR9tU0xxXxUzAaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpPp', 'Mr.', 'Steven',             'Conklin',    '+1',   '5557040704', '1970-07-04', 'American'),
('conrad.fisher@yahoo.com',       '$2b$12$KxQnN5vlQP8rS0uV1yyYyVaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqQq', 'Mr.', 'Conrad',             'Fisher',     '+1',   '5552020704', '2002-07-04', 'American'),
('jeremiah.fisher@yahoo.com',     '$2b$12$LyRoO6wmRQ9sT1vW2zzZzWbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrRr', 'Mr.', 'Jeremiah',           'Fisher',     '+1',   '5552030228', '2003-02-28', 'American'),

('harry.potter@ui.ac.id',           '$2b$12$MzSpP7xoSR0tU2wX3aaAaXcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsSs', 'Mr.', 'Harry',              'Potter',     '+44',  '7921234567', '1980-07-31', 'British'),
('hermione.granger@ui.ac.id',       '$2b$12$NaToQ8ypTS1uV3xY4bbBbYdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtTt', 'Ms.', 'Hermione',           'Granger',    '+44',  '7931234567', '1979-09-19', 'British'),
('ron.weasley@ui.ac.id',            '$2b$12$ObUpR9zqUT2vW4yZ5ccCcZeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuUu', 'Mr.', 'Ron',                'Weasley',    '+44',  '7941234567', '1980-03-01', 'British'),
('draco.malfoy@ui.ac.id',           '$2b$12$PcVqS0arVU3wX5zA6ddDdAfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvVv', 'Mr.', 'Draco',              'Malfoy',     '+44',  '7951234567', '1980-06-05', 'British'),
('luna.lovegood@ui.ac.id',          '$2b$12$QdWrT1bsWV4xY6aB7eeEeBgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwWw', 'Ms.', 'Luna',               'Lovegood',   '+44',  '7961234567', '1981-02-13', 'British'),
('oliver.wood@ui.ac.id',            '$2b$12$ReXsU2ctXW5yZ7bC8ffFfChIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxXx', 'Mr.', 'Oliver',             'Wood',       '+44',  '7971234567', '1975-01-15', 'British');


CREATE TABLE TIER (
    id_tier                     VARCHAR(10)     PRIMARY KEY,
    nama                        VARCHAR(50)      NOT NULL,
    minimal_frekuensi_terbang   INT              NOT NULL,
    minimal_tier_miles          INT              NOT NULL
); 


INSERT INTO TIER (id_tier, nama, minimal_frekuensi_terbang, minimal_tier_miles) VALUES
('TIR-BLU',  'Blue',    0,    0),
('TIR-SLV',  'Silver',   25,   25000),
('TIR-GLD',  'Gold',     50,   50000),
('TIR-PLT',  'Platinum', 100,  100000);


CREATE SEQUENCE MEMBER_NO_SEQ
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


CREATE TABLE MEMBER (
    email               VARCHAR(100)   PRIMARY KEY,
    nomor_member        VARCHAR(20)     NOT NULL        UNIQUE,
    tanggal_bergabung   DATE            NOT NULL,
    id_tier             VARCHAR(10)     NOT NULL,
    award_miles         INT             DEFAULT 0,
    total_miles         INT             DEFAULT 0,
    FOREIGN KEY (email) REFERENCES PENGGUNA(email),
    FOREIGN KEY (id_tier) REFERENCES TIER(id_tier)
);


ALTER TABLE MEMBER
ALTER COLUMN nomor_member SET DEFAULT 'M' || LPAD(nextval('MEMBER_NO_SEQ')::text, 4, '0');


CREATE TRIGGER trigger_cek_tier_member
BEFORE UPDATE ON member
FOR EACH ROW EXECUTE FUNCTION fungsi_update_tier_member();


INSERT INTO MEMBER (email, tanggal_bergabung, id_tier, award_miles, total_miles) VALUES
('strawberry.shortcake@gmail.com',       '2023-01-10', 'TIR-BLU',   1200,   3500),
('blueberry.muffin@gmail.com',           '2023-02-14', 'TIR-BLU',    800,   2100),
('orange.blossom@gmail.com',             '2023-03-22', 'TIR-BLU',   2300,   4800),
('lemon.merringue@gmail.com',            '2023-04-05', 'TIR-BLU',    500,   1500),
('plum.pudding@gmail.com',               '2023-05-18', 'TIR-BLU',   3100,   6200),
('cherry.jam@gmail.com',                 '2023-06-30', 'TIR-BLU',   1750,   4100),
('raspberry.torte@gmail.com',            '2023-07-11', 'TIR-BLU',    950,   2700),
('judy.hopps@yahoo.com',                 '2023-08-19', 'TIR-BLU',   2600,   5500),
('nick.wilde@yahoo.com',                 '2023-09-03', 'TIR-BLU',   1400,   3800),
('fru.fru@yahoo.com',                    '2023-10-27', 'TIR-BLU',    300,    900),
('pawbert.linxley@yahoo.com',            '2023-11-14', 'TIR-BLU',   4200,   9800),
('choso.kamo@gmail.com',                 '2023-12-01', 'TIR-BLU',   3700,   8300),
('hiromi.hiruguma@gmail.com',            '2024-01-08', 'TIR-BLU',   1100,   2900),
('yuji.itadori@gmail.com',               '2024-02-22', 'TIR-BLU',   2900,   6700),
('megumi.fushiguro@gmail.com',           '2024-03-15', 'TIR-BLU',   4800,  11200),
('nobara.kugisaki@gmail.com',            '2024-04-09', 'TIR-BLU',   3300,   7600),
('will.byers@gmail.com',                 '2024-05-20', 'TIR-BLU',    650,   1800),
('holly.wheeler@gmail.com',              '2024-06-11', 'TIR-BLU',    200,    600),
('erica.sinclair@gmail.com',             '2024-07-04', 'TIR-BLU',   1900,   4400),
('peter.parker@gmail.com',               '2024-08-30', 'TIR-BLU',   4500,  10500),

('suguru.geto@gmail.com',                '2022-03-01', 'TIR-SLV',   8200,  27000),
('toji.fushiguro@gmail.com',             '2022-04-17', 'TIR-SLV',  11500,  33800),
('kento.nanami@gmail.com',               '2022-05-29', 'TIR-SLV',   9800,  30200),
('shoko.ieiri@gmail.com',                '2022-06-12', 'TIR-SLV',  14300,  41500),
('yuki.tsukumo@gmail.com',               '2022-07-25', 'TIR-SLV',  12600,  36900),
('yuta.okkotsu@gmail.com',               '2022-08-08', 'TIR-SLV',   7700,  25400),
('maki.zenin@gmail.com',                 '2022-09-19', 'TIR-SLV',  10100,  31700),
('twilight.sparkle@yahoo.com',           '2022-10-31', 'TIR-SLV',  13800,  39200),
('pinkie.pie@yahoo.com',                 '2022-11-14', 'TIR-SLV',   6900,  26800),
('rainbow.dash@yahoo.com',               '2022-12-02', 'TIR-SLV',  15200,  44700),
('jonathan.byers@gmail.com',             '2023-01-25', 'TIR-SLV',   8800,  28500),
('mike.wheeler@gmail.com',               '2023-02-17', 'TIR-SLV',   9400,  29900),
('nancy.wheeler@gmail.com',              '2023-03-08', 'TIR-SLV',  11900,  35600),
('lucas.sinclair@gmail.com',             '2023-04-20', 'TIR-SLV',  13100,  38300),
('dustin.henderson@gmail.com',           '2023-05-05', 'TIR-SLV',   7200,  25100),

('satoru.gojo@gmail.com',                '2021-01-15', 'TIR-GLD',  28000,  72000),
('bruce.banner@gmail.com',               '2021-03-22', 'TIR-GLD',  35500,  89300),
('natasha.romanoff@gmail.com',           '2021-05-09', 'TIR-GLD',  22800,  61500),
('wanda.maximoff@gmail.com',             '2021-07-31', 'TIR-GLD',  31200,  79600),
('scott.lang@gmail.com',                 '2021-09-14', 'TIR-GLD',  27600,  70200),
('steve.harrington@gmail.com',           '2021-11-03', 'TIR-GLD',  24100,  63800),
('max.mayfield@gmail.com',               '2022-01-27', 'TIR-GLD',  38900,  96200),
('jane.hopper@gmail.com',                '2022-03-18', 'TIR-GLD',  21500,  57900),
('larajean.songcovey@ui.ac.id',          '2022-05-07', 'TIR-GLD',  33700,  85400),
('margot.songcovey@ui.ac.id',            '2022-07-22', 'TIR-GLD',  29400,  75100),

('tony.stark@gmail.com',                 '2020-01-01', 'TIR-PLT', 185000, 420000),
('steve.rogers@gmail.com',               '2020-03-15', 'TIR-PLT', 142000, 310000),
('kitty.songcovey@ui.ac.id',             '2020-06-28', 'TIR-PLT', 108500, 235000),
('peter.kavinsky@ui.ac.id',              '2020-09-10', 'TIR-PLT', 167300, 380500),
('josh.sanderson@ui.ac.id',              '2020-12-05', 'TIR-PLT', 129800, 275200);


SELECT setval('MEMBER_NO_SEQ', 50, true);


CREATE SEQUENCE PENYEDIA_ID_SEQ
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


CREATE TABLE PENYEDIA (
    id      INT     NOT NULL    DEFAULT nextval('penyedia_id_seq')      PRIMARY KEY
);


INSERT INTO PENYEDIA DEFAULT VALUES;
INSERT INTO PENYEDIA DEFAULT VALUES;
INSERT INTO PENYEDIA DEFAULT VALUES;
INSERT INTO PENYEDIA DEFAULT VALUES;
INSERT INTO PENYEDIA DEFAULT VALUES;
INSERT INTO PENYEDIA DEFAULT VALUES;
INSERT INTO PENYEDIA DEFAULT VALUES;
INSERT INTO PENYEDIA DEFAULT VALUES;
INSERT INTO PENYEDIA DEFAULT VALUES;
INSERT INTO PENYEDIA DEFAULT VALUES;


SELECT setval('PENYEDIA_ID_SEQ', 10, true);


CREATE TABLE MASKAPAI (
    kode_maskapai       VARCHAR(10)     PRIMARY KEY,
    nama_maskapai       VARCHAR(100)    NOT NULL,
    id_penyedia         INT             NOT NULL,
    FOREIGN KEY (id_penyedia) REFERENCES PENYEDIA (id)
);


INSERT INTO MASKAPAI (kode_maskapai, nama_maskapai, id_penyedia) VALUES 
('GA',  'Garuda Indonesia',     1),
('QG',  'Citilink',             2),
('JT',  'Lion Air',             3),
('SJ',  'Sriwijaya Air',        4),
('ID',  'Batik Air',            5);


CREATE SEQUENCE STAF_ID_SEQ
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


CREATE TABLE STAF (
    email               VARCHAR(100)        PRIMARY KEY,
    id_staf             VARCHAR(20)         NOT NULL UNIQUE DEFAULT 'S' || LPAD(nextval('STAF_ID_SEQ')::text, 4, '0'),
    kode_maskapai       VARCHAR(10)         NOT NULL,
    FOREIGN KEY (email) REFERENCES PENGGUNA (email),
    FOREIGN KEY (kode_maskapai) REFERENCES MASKAPAI (kode_maskapai)    
);


INSERT INTO STAF (email, kode_maskapai) VALUES
('harry.potter@ui.ac.id',       'GA'),
('hermione.granger@ui.ac.id',   'GA'),
('ron.weasley@ui.ac.id',        'QG'),
('draco.malfoy@ui.ac.id',       'QG'),
('luna.lovegood@ui.ac.id',      'JT'),
('oliver.wood@ui.ac.id',        'JT'),
('isabel.conklin@yahoo.com',    'SJ'),
('steven.conklin@yahoo.com',    'SJ'),
('conrad.fisher@yahoo.com',     'ID'),
('jeremiah.fisher@yahoo.com',   'ID');


CREATE TABLE MITRA (
    email_mitra             VARCHAR(100)        PRIMARY KEY,
    id_penyedia             INT                 NOT NULL UNIQUE,
    nama_mitra              VARCHAR(100)        NOT NULL,
    tanggal_kerja_sama      DATE                NOT NULL,
    FOREIGN KEY (id_penyedia) REFERENCES PENYEDIA (id) ON DELETE CASCADE
);


INSERT INTO MITRA (email_mitra, id_penyedia, nama_mitra, tanggal_kerja_sama) VALUES
('partnership.hotelmulia@gmail.com',    6,  'Hotel Mulia',       '2021-03-15'),
('partnership.tiketcom@gmail.com',      7,  'Tiket.com',         '2021-07-01'),
('partnership.gojek@gmail.com',         8,  'Gojek',             '2022-01-10'),
('partnership.avisrentcar@gmail.com',   9,  'Avis Rent a Car',   '2022-06-20'),
('partnership.bca@gmail.com',          10,  'Bank Central Asia', '2023-02-28');

CREATE TABLE IDENTITAS (
    nomor               VARCHAR(50)     PRIMARY KEY,
    email_member        VARCHAR(100)    NOT NULL,
    tanggal_habis       DATE            NOT NULL,
    tanggal_terbit      DATE            NOT NULL,
    negara_penerbit     VARCHAR(50)     NOT NULL,
    jenis               VARCHAR(30)     NOT NULL CHECK (jenis IN ('Paspor', 'KTP', 'SIM')),
    FOREIGN KEY (email_member) REFERENCES MEMBER (email) ON DELETE CASCADE
);


INSERT INTO IDENTITAS (nomor, email_member, tanggal_habis, tanggal_terbit, negara_penerbit, jenis) VALUES
('US-KTP-001', 'strawberry.shortcake@gmail.com', '9999-12-31', '2007-06-15', 'United States', 'KTP'),
('US-KTP-002', 'blueberry.muffin@gmail.com',     '9999-12-31', '2008-03-20', 'United States', 'KTP'),
('US-KTP-003', 'orange.blossom@gmail.com',        '9999-12-31', '2006-10-05', 'United States', 'KTP'),
('US-KTP-004', 'lemon.merringue@gmail.com',       '9999-12-31', '2009-07-22', 'United States', 'KTP'),
('US-KTP-005', 'plum.pudding@gmail.com',          '9999-12-31', '2005-12-01', 'United States', 'KTP'),
('US-KTP-006', 'cherry.jam@gmail.com',            '9999-12-31', '2010-04-30', 'United States', 'KTP'),
('US-KTP-007', 'raspberry.torte@gmail.com',       '9999-12-31', '2007-09-14', 'United States', 'KTP'),
('US-KTP-008', 'judy.hopps@yahoo.com',            '9999-12-31', '2011-11-03', 'United States', 'KTP'),
('US-KTP-009', 'nick.wilde@yahoo.com',            '9999-12-31', '2002-06-22', 'United States', 'KTP'),
('US-KTP-010', 'fru.fru@yahoo.com',               '9999-12-31', '2013-02-14', 'United States', 'KTP'),
('US-KTP-011', 'pawbert.linxley@yahoo.com',       '9999-12-31', '1997-05-19', 'United States', 'KTP'),
('US-KTP-012', 'will.byers@gmail.com',            '9999-12-31', '1988-03-22', 'United States', 'KTP'),

('US-SIM-001', 'holly.wheeler@gmail.com',         '2029-03-10', '2024-03-10', 'United States', 'SIM'),
('US-SIM-002', 'erica.sinclair@gmail.com',        '2028-07-22', '2023-07-22', 'United States', 'SIM'),
('US-SIM-003', 'peter.parker@gmail.com',          '2029-08-10', '2024-08-10', 'United States', 'SIM'),
('US-SIM-004', 'jonathan.byers@gmail.com',        '2028-12-01', '2023-12-01', 'United States', 'SIM'),
('US-SIM-005', 'mike.wheeler@gmail.com',          '2029-04-07', '2024-04-07', 'United States', 'SIM'),
('US-SIM-006', 'nancy.wheeler@gmail.com',         '2028-11-14', '2023-11-14', 'United States', 'SIM'),
('US-SIM-007', 'lucas.sinclair@gmail.com',        '2029-06-01', '2024-06-01', 'United States', 'SIM'),
('US-SIM-008', 'twilight.sparkle@yahoo.com',      '2029-10-22', '2024-10-22', 'United States', 'SIM'),
('US-SIM-009', 'pinkie.pie@yahoo.com',            '2028-05-03', '2023-05-03', 'United States', 'SIM'),
('US-SIM-010', 'rainbow.dash@yahoo.com',          '2029-04-01', '2024-04-01', 'United States', 'SIM'),
('US-SIM-011', 'bruce.banner@gmail.com',          '2028-12-18', '2023-12-18', 'United States', 'SIM'),
('US-SIM-012', 'scott.lang@gmail.com',            '2029-04-15', '2024-04-15', 'United States', 'SIM'),

('JP-PP-001',  'hiromi.hiruguma@gmail.com',       '2026-08-15', '2016-08-15', 'Japan', 'Paspor'),
('JP-PP-002',  'yuji.itadori@gmail.com',          '2027-03-20', '2017-03-20', 'Japan', 'Paspor'),
('JP-PP-003',  'megumi.fushiguro@gmail.com',      '2027-12-22', '2017-12-22', 'Japan', 'Paspor'),
('JP-PP-004',  'nobara.kugisaki@gmail.com',       '2028-08-07', '2018-08-07', 'Japan', 'Paspor'),
('JP-PP-005',  'yuta.okkotsu@gmail.com',          '2027-03-07', '2017-03-07', 'Japan', 'Paspor'),
('JP-PP-006',  'maki.zenin@gmail.com',            '2028-01-20', '2018-01-20', 'Japan', 'Paspor');


CREATE SEQUENCE AWARD_MILES_PACKAGE_ID START 1;


CREATE TABLE AWARD_MILES_PACKAGE (
    id VARCHAR(20) PRIMARY KEY,
    harga_paket DECIMAL(15,2) NOT NULL,
    jumlah_award_miles INT NOT NULL
);


CREATE or replace FUNCTION generate_id_award_miles_package() RETURNS trigger AS $$
BEGIN
    IF NEW.id IS NULL THEN
        NEW.id := 'AMP-' || LPAD(nextval('AWARD_MILES_PACKAGE_ID')::text, 3, '0');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER award_miles_package_id_trigger
BEFORE INSERT ON award_miles_package
FOR EACH ROW
EXECUTE FUNCTION generate_id_award_miles_package();


INSERT INTO AWARD_MILES_PACKAGE (harga_paket, jumlah_award_miles) 
VALUES 
    (150000.00, 1000),
    (650000.00, 5000),
    (1250000.00, 10000),
    (2800000.00, 25000),
    (5200000.00, 50000);


CREATE TABLE MEMBER_AWARD_MILES_PACKAGE(
    id_award_miles_package VARCHAR(20),
    email_member VARCHAR(100),
    timestamp timestamp,

    PRIMARY KEY (id_award_miles_package, email_member, timestamp),
    FOREIGN KEY (id_award_miles_package) REFERENCES AWARD_MILES_PACKAGE(id),
    FOREIGN KEY (email_member) REFERENCES MEMBER(email) ON DELETE CASCADE
);


CREATE OR REPLACE FUNCTION fn_sinkronisasi_award_miles_package()
RETURNS TRIGGER AS $$
DECLARE
    v_jumlah_award_miles INT;
BEGIN
    SELECT jumlah_award_miles
    INTO v_jumlah_award_miles
    FROM AWARD_MILES_PACKAGE
    WHERE id = NEW.id_award_miles_package;

    UPDATE MEMBER
    SET award_miles = award_miles + v_jumlah_award_miles,
        total_miles = total_miles + v_jumlah_award_miles
    WHERE email = NEW.email_member;

    RAISE NOTICE 'SUKSES: Pembelian package berhasil. Award miles dan total miles Anda bertambah % miles.',
        v_jumlah_award_miles;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE TRIGGER trg_sinkronisasi_award_miles_package
AFTER INSERT ON MEMBER_AWARD_MILES_PACKAGE
FOR EACH ROW
EXECUTE FUNCTION fn_sinkronisasi_award_miles_package();


CREATE TABLE BANDARA(
    iata_code CHAR(3) PRIMARY KEY,
    nama VARCHAR(100) NOT NULL,
    kota VARCHAR(100) NOT NULL,
    negara VARCHAR(100) NOT NULL
);


INSERT INTO BANDARA (iata_code, nama, kota, negara) 
VALUES 
    ('CGK', 'Soekarno-Hatta International Airport', 'Jakarta', 'Indonesia'),
    ('DPS', 'Ngurah Rai International Airport', 'Bali', 'Indonesia'),
    ('SUB', 'Juanda International Airport', 'Surabaya', 'Indonesia'),
    ('KNO', 'Kualanamu International Airport', 'Medan', 'Indonesia'),
    ('YIA', 'Yogyakarta International Airport', 'Yogyakarta', 'Indonesia'),
    ('SIN', 'Changi Airport', 'Singapore', 'Singapore'),
    ('KUL', 'Kuala Lumpur International Airport', 'Kuala Lumpur', 'Malaysia'),
    ('BKK', 'Suvarnabhumi Airport', 'Bangkok', 'Thailand'),
    ('HND', 'Haneda Airport', 'Tokyo', 'Japan'),
    ('ICN', 'Incheon International Airport', 'Seoul', 'South Korea'),
    ('DXB', 'Dubai International Airport', 'Dubai', 'United Arab Emirates'),
    ('LHR', 'Heathrow Airport', 'London', 'United Kingdom'),
    ('CDG', 'Charles de Gaulle Airport', 'Paris', 'France'),
    ('JFK', 'John F. Kennedy International Airport', 'New York', 'United States'),
    ('SYD', 'Sydney Kingsford Smith Airport', 'Sydney', 'Australia');


CREATE TABLE CLAIM_MISSING_MILES(
    id SERIAL PRIMARY KEY,
    email_member VARCHAR(100) NOT NULL,
    email_staf VARCHAR(100), 
    maskapai VARCHAR(10) NOT NULL,
    bandara_asal VARCHAR(3) NOT NULL,
    bandara_tujuan VARCHAR(3) NOT NULL,
    tanggal_penerbangan DATE NOT NULL,
    flight_number VARCHAR(10) NOT NULL,
    nomor_tiket VARCHAR(20) NOT NULL,
    kelas_kabin VARCHAR(20) NOT NULL CHECK (kelas_kabin IN ('Economy', 'Business', 'First')),
    pnr VARCHAR(10) NOT NULL,
    status_penerimaan VARCHAR(20) NOT NULL DEFAULT 'Menunggu' CHECK (status_penerimaan IN ('Menunggu', 'Disetujui', 'Ditolak')),
    timestamp timestamp NOT NULL, 

    FOREIGN KEY (email_member) REFERENCES MEMBER(email) ON DELETE CASCADE,
    FOREIGN KEY (email_staf) REFERENCES STAF(email),
    FOREIGN KEY (maskapai) REFERENCES MASKAPAI(kode_maskapai), 
    FOREIGN KEY (bandara_asal) REFERENCES BANDARA(iata_code),
    FOREIGN KEY (bandara_tujuan) REFERENCES BANDARA(iata_code),
    UNIQUE (email_member, flight_number, tanggal_penerbangan, nomor_tiket)
);


CREATE OR REPLACE FUNCTION fn_sync_miles_klaim_disetujui()
RETURNS TRIGGER AS $$
DECLARE
    v_email_member VARCHAR(100);
    v_flight_number VARCHAR(10);
BEGIN
    IF NEW.status_penerimaan = 'Disetujui' AND OLD.status_penerimaan <> 'Disetujui' THEN

        v_email_member := NEW.email_member;
        v_flight_number := NEW.flight_number;

        UPDATE MEMBER
        SET award_miles = award_miles + 1000,
            total_miles = total_miles + 1000
        WHERE email = v_email_member;

        RAISE NOTICE 'SUKSES: Total miles Member "%" telah diperbarui. Miles ditambahkan: 1000 miles dari klaim penerbangan "%".',
            v_email_member, v_flight_number;

    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER trg_sync_miles_klaim_disetujui
AFTER UPDATE OF status_penerimaan ON CLAIM_MISSING_MILES
FOR EACH ROW
EXECUTE FUNCTION fn_sync_miles_klaim_disetujui();


CREATE OR REPLACE FUNCTION sp_top5_member_total_miles()
RETURNS TABLE (
    peringkat       INT,
    email_member    VARCHAR(100),
    total_miles     INT
) AS $$
DECLARE
    v_top1_email VARCHAR(100);
    v_top1_miles INT;
BEGIN
    SELECT m.email, m.total_miles
    INTO v_top1_email, v_top1_miles
    FROM MEMBER m
    ORDER BY m.total_miles DESC
    LIMIT 1;

    RAISE NOTICE 'SUKSES: Daftar Top 5 Member berdasarkan total miles berhasil diperbarui, dengan peringkat pertama "%" memiliki % miles.',
        v_top1_email, v_top1_miles;

    RETURN QUERY
        SELECT
            ROW_NUMBER() OVER (ORDER BY m.total_miles DESC)::INT AS peringkat,
            m.email AS email_member,
            m.total_miles
        FROM MEMBER m
        ORDER BY m.total_miles DESC
        LIMIT 5;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION cek_duplikat_klaim_missing_miles()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 
        FROM claim_missing_miles 
        WHERE flight_number = NEW.flight_number 
            AND tanggal_penerbangan = NEW.tanggal_penerbangan 
            AND nomor_tiket = NEW.nomor_tiket 
            AND email_member = NEW.email_member
    ) THEN
        RAISE EXCEPTION 'ERROR: Klaim untuk penerbangan \"%" pada tanggal \"%" dengan nomor tiket \"%" sudah pernah diajukan sebelumnya.', 
            NEW.flight_number, NEW.tanggal_penerbangan, NEW.nomor_tiket;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER trigger_check_duplicate_claim_missing_miles
BEFORE INSERT ON claim_missing_miles
FOR EACH ROW EXECUTE FUNCTION cek_duplikat_klaim_missing_miles();


INSERT INTO CLAIM_MISSING_MILES (
    email_member, email_staf, maskapai, bandara_asal, bandara_tujuan, 
    tanggal_penerbangan, flight_number, nomor_tiket, kelas_kabin, pnr, 
    status_penerimaan, timestamp
) VALUES 
('strawberry.shortcake@gmail.com', 'harry.potter@ui.ac.id', 'GA', 'CGK', 'DPS', '2023-12-01', 'GA404', '1260000001', 'Economy', 'ABCDEF', 'Disetujui', '2023-12-01 10:00:00'),
('blueberry.muffin@gmail.com', NULL, 'QG', 'SUB', 'CGK', '2024-01-10', 'QG712', '1260000002', 'Economy', 'QWERTY', 'Menunggu', '2024-01-10 14:30:00'),
('orange.blossom@gmail.com', 'luna.lovegood@ui.ac.id', 'JT', 'KNO', 'SIN', '2024-02-15', 'JT202', '1260000003', 'Business', 'ZXCVBN', 'Ditolak', '2024-02-15 09:15:00'),
('suguru.geto@gmail.com', 'isabel.conklin@yahoo.com', 'SJ', 'YIA', 'KUL', '2024-03-20', 'SJ055', '1260000004', 'Economy', 'POIUYT', 'Disetujui', '2024-03-20 16:45:00'),
('satoru.gojo@gmail.com', 'conrad.fisher@yahoo.com', 'ID', 'CGK', 'HND', '2024-04-05', 'ID888', '1260000005', 'First', 'LKJHGF', 'Disetujui', '2024-04-05 23:00:00'),
('tony.stark@gmail.com', 'hermione.granger@ui.ac.id', 'GA', 'JFK', 'LHR', '2024-05-12', 'GA909', '1260000006', 'First', 'MNBVCX', 'Disetujui', '2024-05-12 08:00:00'),
('steve.rogers@gmail.com', NULL, 'GA', 'LHR', 'CDG', '2024-06-01', 'GA910', '1260000007', 'Business', 'ASDFGH', 'Menunggu', '2024-06-01 11:20:00'),
('bruce.banner@gmail.com', 'draco.malfoy@ui.ac.id', 'QG', 'DPS', 'BKK', '2024-06-15', 'QG555', '1260000008', 'Economy', 'YTREWQ', 'Ditolak', '2024-06-15 13:40:00'),
('yuji.itadori@gmail.com', 'oliver.wood@ui.ac.id', 'JT', 'SUB', 'DPS', '2024-07-02', 'JT333', '1260000009', 'Economy', 'PLMOKN', 'Disetujui', '2024-07-02 07:10:00'),
('megumi.fushiguro@gmail.com', 'steven.conklin@yahoo.com', 'SJ', 'CGK', 'SUB', '2024-07-20', 'SJ111', '1260000010', 'Economy', 'IJUHBY', 'Disetujui', '2024-07-20 18:30:00'),
('wanda.maximoff@gmail.com', 'jeremiah.fisher@yahoo.com', 'ID', 'DXB', 'CGK', '2024-08-05', 'ID777', '1260000011', 'Business', 'YGVTFC', 'Ditolak', '2024-08-05 02:15:00'),
('peter.parker@gmail.com', NULL, 'GA', 'JFK', 'SYD', '2024-08-15', 'GA101', '1260000012', 'Economy', 'RDXESZ', 'Menunggu', '2024-08-15 06:45:00'),
('kitty.songcovey@ui.ac.id', 'harry.potter@ui.ac.id', 'GA', 'ICN', 'CGK', '2024-09-01', 'GA878', '1260000013', 'Business', 'WAQZSE', 'Disetujui', '2024-09-01 10:50:00'),
('nancy.wheeler@gmail.com', 'ron.weasley@ui.ac.id', 'QG', 'CGK', 'YIA', '2024-09-10', 'QG222', '1260000014', 'Economy', 'QAZWSX', 'Disetujui', '2024-09-10 15:20:00'),
('dustin.henderson@gmail.com', 'luna.lovegood@ui.ac.id', 'JT', 'KNO', 'CGK', '2024-10-05', 'JT444', '1260000015', 'Economy', 'EDCRFV', 'Ditolak', '2024-10-05 12:00:00'),
('shoko.ieiri@gmail.com', NULL, 'SJ', 'DPS', 'SUB', '2024-10-20', 'SJ666', '1260000016', 'Economy', 'TGBYHN', 'Menunggu', '2024-10-20 09:30:00'),
('maki.zenin@gmail.com', 'conrad.fisher@yahoo.com', 'ID', 'HND', 'SIN', '2024-11-01', 'ID999', '1260000017', 'Business', 'UJMILK', 'Disetujui', '2024-11-01 14:10:00'),
('rainbow.dash@yahoo.com', 'hermione.granger@ui.ac.id', 'GA', 'CGK', 'SYD', '2024-11-15', 'GA202', '1260000018', 'First', 'OKMNNB', 'Disetujui', '2024-11-15 22:45:00'),
('peter.kavinsky@ui.ac.id', 'draco.malfoy@ui.ac.id', 'QG', 'SUB', 'DPS', '2024-12-05', 'QG888', '1260000019', 'Economy', 'IJNBHU', 'Disetujui', '2024-12-05 08:25:00'),
('josh.sanderson@ui.ac.id', NULL, 'JT', 'CGK', 'KNO', '2024-12-20', 'JT101', '1260000020', 'Economy', 'UHBVGY', 'Menunggu', '2024-12-20 17:00:00');


INSERT INTO MEMBER_AWARD_MILES_PACKAGE (id_award_miles_package, email_member, timestamp) 
VALUES 
    ('AMP-001', 'strawberry.shortcake@gmail.com', '2024-01-15 10:30:00'),
    ('AMP-002', 'blueberry.muffin@gmail.com', '2024-01-20 14:15:00'),
    ('AMP-003', 'orange.blossom@gmail.com', '2024-02-05 09:00:00'),
    ('AMP-001', 'judy.hopps@yahoo.com', '2024-02-14 16:45:00'),
    ('AMP-004', 'nick.wilde@yahoo.com', '2024-03-01 11:20:00'),
    
    ('AMP-005', 'choso.kamo@gmail.com', '2024-03-10 08:30:00'),
    ('AMP-002', 'yuji.itadori@gmail.com', '2024-03-25 13:10:00'),
    ('AMP-003', 'megumi.fushiguro@gmail.com', '2024-04-02 15:55:00'),
    ('AMP-001', 'will.byers@gmail.com', '2024-04-18 10:05:00'),
    ('AMP-004', 'peter.parker@gmail.com', '2024-05-01 12:00:00'),
    
    ('AMP-005', 'suguru.geto@gmail.com', '2024-05-12 14:40:00'),
    ('AMP-002', 'kento.nanami@gmail.com', '2024-05-20 09:25:00'),
    ('AMP-003', 'shoko.ieiri@gmail.com', '2024-06-05 16:15:00'),
    ('AMP-001', 'rainbow.dash@yahoo.com', '2024-06-15 11:50:00'),
    ('AMP-004', 'nancy.wheeler@gmail.com', '2024-07-01 10:10:00'),
    
    ('AMP-005', 'satoru.gojo@gmail.com', '2024-07-10 13:35:00'),
    ('AMP-002', 'bruce.banner@gmail.com', '2024-08-05 08:45:00'),
    ('AMP-003', 'wanda.maximoff@gmail.com', '2024-08-20 15:20:00'),
    ('AMP-001', 'tony.stark@gmail.com', '2024-09-01 11:00:00'),
    ('AMP-005', 'steve.rogers@gmail.com', '2024-09-15 14:30:00');


CREATE TABLE TRANSFER (
    email_member_1           VARCHAR(100)   NOT NULL,
    email_member_2           VARCHAR(100)   NOT NULL,
    timestamp                timestamp,      
    jumlah                   INT            NOT NULL, 
    catatan                  VARCHAR(255),  
    PRIMARY KEY (email_member_1, email_member_2, timestamp),
    FOREIGN KEY (email_member_1) REFERENCES MEMBER(email) ON DELETE CASCADE,
    FOREIGN KEY (email_member_2) REFERENCES MEMBER(email) ON DELETE CASCADE,
    CHECK (email_member_1 <> email_member_2)
);


CREATE OR REPLACE FUNCTION proses_transfer_miles()
RETURNS TRIGGER AS $$
DECLARE
    v_saldo_pengirim INT;
BEGIN
    SELECT award_miles INTO v_saldo_pengirim 
    FROM MEMBER 
    WHERE email = NEW.email_member_1;

    IF v_saldo_pengirim < NEW.jumlah THEN
        RAISE EXCEPTION 'ERROR: Saldo award miles tidak mencukupi. Saldo Anda saat ini: % miles, jumlah transfer: % miles.', 
        v_saldo_pengirim, NEW.jumlah;
    END IF;

    UPDATE MEMBER 
    SET award_miles = award_miles - NEW.jumlah 
    WHERE email = NEW.email_member_1;

    UPDATE MEMBER 
    SET award_miles = award_miles + NEW.jumlah
    WHERE email = NEW.email_member_2;

    IF NEW.timestamp IS NULL THEN
        NEW.timestamp := CURRENT_TIMESTAMP;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER trg_transfer_miles
BEFORE INSERT ON TRANSFER
FOR EACH ROW
EXECUTE FUNCTION proses_transfer_miles();


CREATE OR REPLACE FUNCTION fn_transfer_miles(
    p_email_pengirim VARCHAR,
    p_email_penerima VARCHAR,
    p_jumlah INT,
    p_catatan VARCHAR
) RETURNS TEXT
AS $$
DECLARE
    result TEXT;
BEGIN
    INSERT INTO TRANSFER (email_member_1, email_member_2, jumlah, catatan)
    VALUES (p_email_pengirim, p_email_penerima, p_jumlah, p_catatan);

    result := FORMAT('SUKSES: Transfer %s miles dari "%s" ke "%s" berhasil dicatat.', 
        p_jumlah, p_email_pengirim, p_email_penerima);
    RETURN result;

EXCEPTION
    WHEN OTHERS THEN
        RETURN FORMAT('ERROR: %', SQLERRM);
END;
$$ LANGUAGE plpgsql;


INSERT INTO TRANSFER (email_member_1, email_member_2, timestamp, jumlah, catatan) VALUES

('tony.stark@gmail.com', 'peter.parker@gmail.com', '2025-01-10 09:15:00', 5000, 'Dana tambahan untuk perlengkapan magang Stark Industries'),
('steve.rogers@gmail.com', 'tony.stark@gmail.com', '2025-01-12 14:30:00', 50, 'Ganti uang kopi dan donat kemarin'),
('bruce.banner@gmail.com', 'tony.stark@gmail.com', '2025-02-05 10:00:00', 1200, 'Ganti rugi peralatan lab yang tidak sengaja rusak'),
('natasha.romanoff@gmail.com', 'wanda.maximoff@gmail.com', '2025-02-14 19:00:00', 300, 'Patungan hadiah ulang tahun Vision'),

('satoru.gojo@gmail.com', 'megumi.fushiguro@gmail.com', '2025-03-01 08:00:00', 2500, 'Uang saku bulanan. Jangan lupa makan enak!'),
('yuji.itadori@gmail.com', 'nobara.kugisaki@gmail.com', '2025-03-05 16:45:00', 150, 'Titip belikan crepes di Harajuku'),
('toji.fushiguro@gmail.com', 'megumi.fushiguro@gmail.com', '2025-04-10 12:00:00', 10000, 'Uang jajan. Jangan bilang-bilang Gojo.'),
('kento.nanami@gmail.com', 'yuji.itadori@gmail.com', '2025-04-15 17:30:00', 800, 'Bonus lembur misi minggu lalu. Kerja bagus.'),

('judy.hopps@yahoo.com', 'nick.wilde@yahoo.com', '2025-05-12 13:20:00', 75, 'Patungan beli Jumbo-pop untuk Pawpsicles'),
('strawberry.shortcake@gmail.com', 'blueberry.muffin@gmail.com', '2025-05-20 10:10:00', 200, 'Beli bahan baku tambahan untuk toko kue'),

('twilight.sparkle@yahoo.com', 'pinkie.pie@yahoo.com', '2025-06-01 15:00:00', 500, 'Modal untuk dekorasi pesta kejutan Applejack'),

('mike.wheeler@gmail.com', 'will.byers@gmail.com', '2025-07-04 20:00:00', 60, 'Beli dadu 20-sisi yang baru untuk kampanye D&D'),
('dustin.henderson@gmail.com', 'steve.harrington@gmail.com', '2025-07-10 21:30:00', 35, 'Uang bensin karena sudah antar jemput malam ini'),
('lucas.sinclair@gmail.com', 'max.mayfield@gmail.com', '2025-08-15 18:00:00', 100, 'Kalah taruhan main Dig Dug di Arcade'),

('larajean.songcovey@ui.ac.id', 'peter.kavinsky@ui.ac.id', '2025-09-05 16:20:00', 45, 'Uang bensin untuk perjalanan ke kampus'),
('kitty.songcovey@ui.ac.id', 'margot.songcovey@ui.ac.id', '2025-09-10 09:00:00', 150, 'Kirim uang jajan dari rumah'),
('josh.sanderson@ui.ac.id', 'margot.songcovey@ui.ac.id', '2025-10-01 12:00:00', 300, 'Kado kecil untuk ulang tahunmu. Miss you!');


CREATE SEQUENCE hadiah_seq START 1;


CREATE TABLE HADIAH (
    kode_hadiah      VARCHAR(20)     PRIMARY KEY,
    nama             VARCHAR(100)    NOT NULL,
    miles            INT             NOT NULL,
    deskripsi        TEXT            ,
    valid_start_date DATE            NOT NULL,
    program_end      DATE            NOT NULL,
    id_penyedia      INT             NOT NULL,
    FOREIGN KEY (id_penyedia) REFERENCES PENYEDIA(id) ON DELETE CASCADE,
    CHECK (kode_hadiah LIKE 'RWD-%')
);


CREATE or replace FUNCTION generate_kode_hadiah() RETURNS trigger AS $$
BEGIN
    IF NEW.kode_hadiah IS NULL THEN
        NEW.kode_hadiah := 'RWD-' || LPAD(nextval('hadiah_seq')::text, 3, '0');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER hadiah_kode_trigger
BEFORE INSERT ON HADIAH
FOR EACH ROW
EXECUTE FUNCTION generate_kode_hadiah();


CREATE OR REPLACE FUNCTION fn_validasi_redeem_hadiah()
RETURNS TRIGGER AS $$
DECLARE
    v_miles_hadiah INT;
    v_nama_hadiah VARCHAR(100);
    v_valid_start DATE;
    v_program_end DATE;
    v_saldo_member INT;
    v_tgl_redeem DATE;
BEGIN
    SELECT nama, miles, valid_start_date, program_end
    INTO v_nama_hadiah, v_miles_hadiah, v_valid_start, v_program_end
    FROM HADIAH
    WHERE kode_hadiah = NEW.kode_hadiah;

    SELECT award_miles
    INTO v_saldo_member
    FROM MEMBER
    WHERE email = NEW.email_member;

    v_tgl_redeem := DATE(NEW.timestamp);

    IF v_tgl_redeem < v_valid_start OR v_tgl_redeem > v_program_end THEN
        RAISE EXCEPTION 'ERROR: Hadiah "%" tidak tersedia pada periode ini.', v_nama_hadiah;
    END IF;

    IF v_saldo_member < v_miles_hadiah THEN
        RAISE EXCEPTION 'ERROR: Saldo award miles tidak mencukupi. Dibutuhkan % miles, saldo Anda: % miles.',
            v_miles_hadiah, v_saldo_member;
    END IF;

    UPDATE MEMBER
    SET award_miles = award_miles - v_miles_hadiah
    WHERE email = NEW.email_member;

    RAISE NOTICE 'SUKSES: Redeem hadiah "%" berhasil. Award miles Anda berkurang % miles.',
        v_nama_hadiah, v_miles_hadiah;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


INSERT INTO HADIAH (nama, miles, deskripsi, valid_start_date, program_end, id_penyedia) VALUES
('Voucher Kopi Rp50.000', 500, 'Nikmati kopi gratis atau potongan harga di gerai partner kami.', '2025-01-01', '2025-12-31', 1),
('Tiket Nonton Bioskop Premiere', 1200, 'Satu tiket nonton film premier di akhir pekan, berlaku di seluruh cabang.', '2025-02-01', '2025-11-30', 2),
('Merchandise Kaos Eksklusif', 2500, 'Kaos edisi terbatas khusus untuk member loyalty program.', '2025-03-01', '2025-12-31', 3),
('Diskon 20% Belanja Supermarket', 800, 'Potongan harga maksimal Rp100.000 untuk belanja bulanan Anda.', '2025-01-15', '2025-05-15', 4),
('Voucher Menginap Hotel Bintang 4', 15000, 'Gratis menginap 1 malam untuk tipe kamar Deluxe (termasuk sarapan).', '2025-06-01', '2025-12-31', 5),
('E-Money Saldo Rp100.000', 1000, 'Top up saldo e-money langsung ke nomor ponsel yang terdaftar.', '2025-01-01', '2026-01-01', 6),
('Paket Liburan Bali 3H2M', 50000, 'Paket tour lengkap ke Bali untuk 1 orang, sudah termasuk tiket pesawat.', '2025-08-01', '2025-12-31', 7),
('Voucher Makan Malam Romantis', 3500, 'Set menu fine dining untuk 2 orang di restoran mitra kami.', '2025-02-10', '2025-03-10', 8),
('Gratis Bagasi Pesawat 10kg', 2000, 'Tambahan kuota bagasi penerbangan domestik untuk kenyamanan liburan Anda.', '2025-01-01', '2025-12-31', 1),
('Akses Airport Premium Lounge', 3000, 'Akses gratis ke premium lounge di bandara selama maksimal 3 jam.', '2025-04-01', '2025-12-31', 2),
('Diskon Sewa Mobil 30%', 1500, 'Potongan untuk penyewaan mobil harian di berbagai kota besar.', '2025-05-01', '2025-10-31', 3),
('Voucher Spa & Pijat 90 Menit', 2200, 'Paket relaksasi komplit di pusat spa eksklusif mitra kami.', '2025-07-01', '2025-12-31', 4);


CREATE TABLE REDEEM (
    email_member         VARCHAR(100)   NOT NULL,
    kode_hadiah          VARCHAR(20)    NOT NULL,
    timestamp            timestamp      NOT NULL,
    PRIMARY KEY (email_member, kode_hadiah, timestamp),
    FOREIGN KEY (email_member) REFERENCES MEMBER(email) ON DELETE CASCADE,
    FOREIGN KEY (kode_hadiah) REFERENCES HADIAH(kode_hadiah)
);


CREATE OR REPLACE TRIGGER trg_validasi_redeem_hadiah
BEFORE INSERT ON REDEEM
FOR EACH ROW
EXECUTE FUNCTION fn_validasi_redeem_hadiah();


INSERT INTO REDEEM (email_member, kode_hadiah, timestamp) VALUES

('tony.stark@gmail.com', 'RWD-007', '2025-08-15 10:00:00'),
('tony.stark@gmail.com', 'RWD-005', '2025-10-20 14:30:00'),
('tony.stark@gmail.com', 'RWD-010', '2025-12-01 09:15:00'),

('steve.rogers@gmail.com', 'RWD-009', '2025-03-10 08:45:00'),
('steve.rogers@gmail.com', 'RWD-011', '2025-05-12 11:20:00'),

('satoru.gojo@gmail.com', 'RWD-005', '2025-06-15 16:00:00'), 
('satoru.gojo@gmail.com', 'RWD-008', '2025-02-20 19:30:00'),

('natasha.romanoff@gmail.com', 'RWD-012', '2025-07-05 13:10:00'),
('wanda.maximoff@gmail.com', 'RWD-008', '2025-02-14 20:00:00'),

('megumi.fushiguro@gmail.com', 'RWD-002', '2025-04-10 18:00:00'),
('yuji.itadori@gmail.com', 'RWD-003', '2025-05-01 10:30:00'), 
('nobara.kugisaki@gmail.com', 'RWD-004', '2025-02-28 15:45:00'), 
('kento.nanami@gmail.com', 'RWD-001', '2025-01-15 07:30:00'),
('shoko.ieiri@gmail.com', 'RWD-012', '2025-09-09 17:00:00'),

('larajean.songcovey@ui.ac.id', 'RWD-004', '2025-03-20 16:15:00'),
('peter.kavinsky@ui.ac.id', 'RWD-006', '2025-04-05 09:00:00'),
('kitty.songcovey@ui.ac.id', 'RWD-002', '2025-06-30 19:00:00'),

('mike.wheeler@gmail.com', 'RWD-003', '2025-06-01 14:20:00'),
('dustin.henderson@gmail.com', 'RWD-001', '2025-08-02 15:10:00'),
('max.mayfield@gmail.com', 'RWD-002', '2025-08-10 20:30:00'),
('jane.hopper@gmail.com', 'RWD-006', '2025-11-11 11:11:00'),

('twilight.sparkle@yahoo.com', 'RWD-002', '2025-05-20 18:45:00'),
('pinkie.pie@yahoo.com', 'RWD-006', '2025-06-05 10:00:00'),
('judy.hopps@yahoo.com', 'RWD-001', '2025-03-15 08:30:00'),
('strawberry.shortcake@gmail.com', 'RWD-004', '2025-02-10 16:00:00'); 