create table IF NOT EXISTS submitted (
    submitted_id        integer primary key autoincrement not null,
    title               text,
    url                 text,
    whensub             text,
    username            text,
    UID                 text
);

create table IF NOT EXISTS chosen (
    chosen_id           integer primary key autoincrement not null,
    chosen_date         text,
    url                 text,
    submitted_id        integer, FOREIGN KEY(submitted_id) references submitted(submitted_id)
);

create table IF NOT EXISTS ineligible (
    ineligible_id       integer primary key autoincrement not null,
    reason              text,
    submitted_id        integer, FOREIGN KEY(submitted_id) references submitted(submitted_id)
);


  
