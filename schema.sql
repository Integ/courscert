drop table if exists certs;
create table certs (
  id integer primary key autoincrement,
  cert_id string not null,
  course_name string not null,
  given_name string not null,
  surname string not null,
  complete_date string not null,
  weeks integer not null,
  min_hours_a_week integer not null,
  max_hours_a_week integer not null,
  teacher_name string not null,
  school_name string not null
);