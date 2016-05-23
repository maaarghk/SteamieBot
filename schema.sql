create table submitter (
  user_id               integer primary key autoincrement not null,
  age                   text,
  name                  text
);

create table submitted (
    submitted_id        integer primary key autoincrement not null,
    name                text,
    url                 text,
    whensub             date,
    comment             text,
    user_id             integer, FOREIGN KEY(user_id) references submitter(user_id)
);

create table chosen (
    id                  integer primary key autoincrement not null,
    submitted_id        integer, FOREIGN KEY(submitted_id) references submitted(submitted_id)
);


  
