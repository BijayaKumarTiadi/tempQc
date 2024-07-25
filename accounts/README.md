
## For accounts Table :

```bash
-- Add missing columns
ALTER TABLE usermaster 
ADD COLUMN last_login DATETIME NULL,
ADD COLUMN is_superuser INT(11) NULL,
ADD COLUMN first_name VARCHAR(150) NULL,
ADD COLUMN last_name VARCHAR(150) NULL,
ADD COLUMN is_staff INT(11) NULL,
ADD COLUMN is_active INT(11) NULL,
ADD COLUMN date_joined DATETIME NULL;

-- Modify existing columns to match schema
ALTER TABLE usermaster 
MODIFY COLUMN UserID VARCHAR(10) NOT NULL PRIMARY KEY,
MODIFY COLUMN UserDepartmentID VARCHAR(10) NULL,
MODIFY COLUMN EmployeeCode VARCHAR(10) NULL,
MODIFY COLUMN UserName VARCHAR(100) NULL,
MODIFY COLUMN UserLoginName VARCHAR(100) NULL UNIQUE,
MODIFY COLUMN UserPassword VARCHAR(50) NULL,
MODIFY COLUMN Post VARCHAR(100) NULL,
MODIFY COLUMN Joining_Date VARCHAR(20) NULL,
MODIFY COLUMN Address VARCHAR(500) NULL,
MODIFY COLUMN City VARCHAR(100) NULL,
MODIFY COLUMN State VARCHAR(100) NULL,
MODIFY COLUMN DateofBirth VARCHAR(20) NULL,
MODIFY COLUMN Ph1 VARCHAR(20) NULL,
MODIFY COLUMN ph2 VARCHAR(20) NULL,
MODIFY COLUMN Fax VARCHAR(20) NULL,
MODIFY COLUMN Email VARCHAR(100) NOT NULL,
MODIFY COLUMN ReferreddBy VARCHAR(100) NULL,
MODIFY COLUMN IsActive TINYINT(3) NULL,
MODIFY COLUMN AUID VARCHAR(50) NULL,
MODIFY COLUMN ADateTime DATETIME NOT NULL DEFAULT '1900-01-01 00:00:00',
MODIFY COLUMN MUID VARCHAR(50) NULL,
MODIFY COLUMN MDateTime VARCHAR(50) NOT NULL,
MODIFY COLUMN CompanyID INT(5) NULL,
MODIFY COLUMN MgtLevels INT(1) NULL DEFAULT 0,
MODIFY COLUMN Icompanyid VARCHAR(10) NULL;

-- Ensure the unique constraint on (UserID, Email)
ALTER TABLE usermaster
ADD CONSTRAINT usermaster_unique UNIQUE (UserID, Email);
```

## For est_itemtypemaster : 
``` bash
-- est_itemtypemaster

-- Add missing columns
ALTER TABLE est_itemtypemaster 
ADD COLUMN carton_cat VARCHAR(20) NOT NULL,
ADD COLUMN imgpath VARCHAR(200) NULL,
ADD COLUMN ecma_code VARCHAR(50) NULL,
ADD COLUMN hover_imgpath VARCHAR(200) NULL;

-- Modify existing columns to match schema
ALTER TABLE est_itemtypemaster 
MODIFY COLUMN ID INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
MODIFY COLUMN CartonType VARCHAR(60) NOT NULL,
MODIFY COLUMN internalCartonType VARCHAR(60) NOT NULL UNIQUE;

-- Add unique constraint for (ID, CartonType)
ALTER TABLE est_itemtypemaster 
ADD CONSTRAINT est_itemtypemaster_unique UNIQUE (ID, CartonType);
```



## Item_womaster table:
``` bash

ALTER TABLE Item_womaster
ADD COLUMN SeriesID VARCHAR(10);

```
## Authors

- [@BijayakumarTiadi](https://www.github.com/BijayakumarTiadi)