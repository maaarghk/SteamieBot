create table submitted (
    submitted_id        integer primary key autoincrement not null,
    name                text,
    url                 text,
    whensub             date,
    comment             text,
    user_id             integer, FOREIGN KEY(username) references submitter(id)
);

create table chosen (
    id                  integer primary key autoincrement not null,
    submitted_id        integer, FOREIGN KEY(submitted_id) references submitted(id)
);

create table submitter (
  user_id               integer primary key autoincrement not null,
  age                   text,
  name                  text
);
  
