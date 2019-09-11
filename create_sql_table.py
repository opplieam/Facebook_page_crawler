import argparse
import psycopg2


def create_table(kwargs):
    commands = (
        """
        CREATE TABLE IF NOT EXISTS posts (
            post_id VARCHAR(80) PRIMARY KEY,
            page_id VARCHAR(40) NOT NULL,
            page_name VARCHAR(50) NOT NULL,
            post_url VARCHAR(100) NOT NULL,
            post_text text,
            video_url VARCHAR(700),
            comment_count INT,
            reaction_count INT,
            share_count INT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS image_urls (
            image_id SERIAL PRIMARY KEY,
            post_id VARCHAR(80) NOT NULL,
            image_url VARCHAR(500) NOT NULL,
            FOREIGN KEY (post_id)
            REFERENCES posts (post_id)
            ON UPDATE CASCADE ON DELETE CASCADE 
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS comments (
            comment_id VARCHAR(100) PRIMARY KEY,
            post_id VARCHAR(80) NOT NULL,
            comment_text text,
            author_name VARCHAR(250) NOT NULL,
            author_id VARCHAR(30) NOT NULL,
            author_url VARCHAR(100) NOT NULL,
            FOREIGN KEY (post_id)
            REFERENCES posts (post_id)
            ON UPDATE CASCADE ON DELETE CASCADE
        )
        """
    )

    try:
        connection = psycopg2.connect(user=kwargs.get('user'),
                                      password=kwargs.get('password'),
                                      host=kwargs.get('host'),
                                      port=kwargs.get('port'),
                                      database=kwargs.get('database'))
        cursor = connection.cursor()
        # Print PostgreSQL Connection properties
        print(connection.get_dsn_parameters(), "\n")
        # Print PostgreSQL version
        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        print("You are connected to - ", record, "\n")

        for command in commands:
            cursor.execute(command)
        connection.commit()
        print('Added posts, image_urls and comments table')

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-a', action='append', dest='collection',
        help='Adding argument'
    )
    results = parser.parse_args()
    kwargs = dict()
    for result in vars(results).get('collection'):
        k_v = result.split('=')
        kwargs[k_v[0]] = k_v[1]

    if not kwargs.get('user') or not kwargs.get('password'):
        exit('Error! Please provide username or password for database')
    if not kwargs.get('host') or not kwargs.get('port'):
        exit('Error! Please provide host or port for database')
    if not kwargs.get('database'):
        exit('Error! Please provide database name')

    create_table(kwargs)
