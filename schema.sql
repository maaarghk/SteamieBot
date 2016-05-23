create table IF NOT EXISTS submitted (
    submitted_id        integer primary key autoincrement not null,
    title               text,
    url                 text,
    whensub             text,
    username            text,
    UID                 text
);

create table IF NOT EXISTS chosen (
    chosen_date         text,
    submitted_id        integer primary key, FOREIGN KEY(submitted_id) references submitted(submitted_id)
);

create table IF NOT EXISTS ineligible (
    reason              text,
    submitted_id        integer primary key, FOREIGN KEY(submitted_id) references submitted(submitted_id)
);


  
