create table IF NOT EXISTS submitted (
    submitted_id        integer primary key autoincrement not null,
    url                 text,
    whensub             text,
    username            text,
);

create table IF NOT EXISTS chosen (
    chosen_date         text primary key,
    url                 text,
    submitted_id        integer,
    FOREIGN KEY(submitted_id) references submitted(submitted_id)
);

  
