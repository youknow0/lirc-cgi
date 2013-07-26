CREATE TABLE commands (
	cmd_id VARCHAR(50),
	dev_id VARCHAR(50) NOT NULL,
	name VARCHAR(50) NOT NULL,
	FOREIGN KEY(dev_id) REFERENCES devices(dev_id),
	PRIMARY KEY(cmd_id, dev_id)
);

CREATE TABLE devices (
	dev_id VARCHAR(50),
	name VARCHAR(50) NOT NULL,
	PRIMARY KEY(dev_id)
);
