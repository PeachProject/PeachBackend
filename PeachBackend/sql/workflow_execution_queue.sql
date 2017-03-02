CREATE TABLE IF NOT EXISTS queue (
    id INT(11) AUTO_INCREMENT PRIMARY KEY,
    user VARCHAR(30),
    execution_file VARCHAR(255) UNIQUE,
    workflow_json TEXT,
    status INT(1),
    progress INT(3),
    original_workflow_file VARCHAR(255),
    sending_date datetime NOT NULL DEFAULT '1000-01-01',
    finished_date datetime NOT NULL DEFAULT '1000-01-01',
    priority INT(1),
    output_file VARCHAR(255)
);
