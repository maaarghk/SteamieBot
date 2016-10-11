create table IF NOT EXISTS submitted (
    submitted_id        integer primary key autoincrement not null,
    url                 text,
    whensub             integer,
    username            text
);

create table IF NOT EXISTS chosen (
    chosen_date         integer primary key,
    url                 text,
    submitted_id        integer,
    FOREIGN KEY(submitted_id) references submitted(submitted_id)
);

  
