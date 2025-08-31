package pg

import (
	"context"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

func New(username, password, host, port, dbname string) *Postgres {
	connString := "postgres://" + username + ":" + password + "@" + host + ":" + port + "/" + dbname + "?pool_max_conns=100"

	ctx := context.Background()
	db, err := pgxpool.New(ctx, connString)
	if err != nil {
		panic(err)
	}

	return &Postgres{db}
}

type Postgres struct {
	db *pgxpool.Pool
}

type txKey struct{}

func (pg *Postgres) CtxWithTx(ctx context.Context) (context.Context, error) {
	tx, err := pg.db.Begin(ctx)
	if err != nil {
		return nil, err
	}
	return context.WithValue(ctx, txKey{}, tx), nil
}

func (pg *Postgres) CommitTx(ctx context.Context) error {
	tx := pg.getTx(ctx)
	err := tx.Commit(ctx)
	if err != nil {
		return err
	}
	return nil
}

func (pg *Postgres) RollbackTx(ctx context.Context) {
	tx := pg.getTx(ctx)
	_ = tx.Rollback(ctx)
}

func (pg *Postgres) getTx(ctx context.Context) pgx.Tx {
	if tx, ok := ctx.Value(txKey{}).(pgx.Tx); ok {
		return tx
	}
	return nil
}

func (pg *Postgres) Insert(ctx context.Context, query string, args ...any) (any, error) {
	var id any
	tx := pg.getTx(ctx)
	if tx != nil {
		err := tx.QueryRow(ctx, query, args...).Scan(&id)
		if err != nil {
			return 0, err
		}
	} else {
		err := pg.db.QueryRow(ctx, query, args...).Scan(&id)
		if err != nil {
			return 0, err
		}
	}
	return id, nil
}

func (pg *Postgres) Select(ctx context.Context, query string, args ...any) (pgx.Rows, error) {
	tx := pg.getTx(ctx)
	if tx != nil {
		return tx.Query(ctx, query, args...)
	}
	return pg.db.Query(ctx, query, args...)
}

func (pg *Postgres) Update(ctx context.Context, query string, args ...any) error {
	tx := pg.getTx(ctx)
	if tx != nil {
		_, err := tx.Exec(ctx, query, args...)
		return err
	}
	_, err := pg.db.Exec(ctx, query, args...)
	return err
}

func (pg *Postgres) Delete(ctx context.Context, query string, args ...any) error {
	tx := pg.getTx(ctx)
	if tx != nil {
		_, err := tx.Exec(ctx, query, args...)
		return err
	}
	_, err := pg.db.Exec(ctx, query, args...)
	return err
}

func (pg *Postgres) CreateTable(ctx context.Context, query string) error {
	tx := pg.getTx(ctx)
	if tx != nil {
		_, err := tx.Exec(ctx, query)
		return err
	}
	_, err := pg.db.Exec(ctx, query)
	return err
}

func (pg *Postgres) DropTable(ctx context.Context, query string) error {
	tx := pg.getTx(ctx)
	if tx != nil {
		_, err := tx.Exec(ctx, query)
		return err
	}
	_, err := pg.db.Exec(ctx, query)
	return err
}
