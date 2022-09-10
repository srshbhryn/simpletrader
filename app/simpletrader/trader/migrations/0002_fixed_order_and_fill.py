# Generated by Django 4.1 on 2022-09-05 17:19

from django.db import migrations, models
import django.db.models.deletion
import simpletrader.trader.models
import timescale.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('trader', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL('''
-- public.trader_order definition

-- Drop table

DROP TABLE public.trader_order;

CREATE TABLE public.trader_order (
	id bigserial NOT NULL,
    exchange_id varchar(32) NOT NULL,
	client_order_id varchar(128) NULL,
	market_id int4 NOT NULL,
	status_id int4 NOT NULL,
	leverage int4 DEFAULT 1,
	"timestamp" timestamptz NOT NULL,
	price numeric(32, 16) NULL,
	volume numeric(32, 16) NOT NULL,
	is_sell bool NOT NULL,
	account_id int8 NOT NULL,
	placed_by_id varchar(4) NOT NULL,
	CONSTRAINT trader_order_account_id_09e7ecee_fk_trader_account_id FOREIGN KEY (account_id) REFERENCES public.trader_account(id) DEFERRABLE INITIALLY DEFERRED,
	CONSTRAINT trader_order_placed_by_id_28faa213_fk_trader_bot_token FOREIGN KEY (placed_by_id) REFERENCES public.trader_bot("token") DEFERRABLE INITIALLY DEFERRED
);
CREATE INDEX trader_order_account_id_09e7ecee ON public.trader_order USING btree (account_id);
CREATE INDEX trader_order_exchange_id_dcdb1512 ON public.trader_order USING btree (exchange_id);
CREATE INDEX trader_order_client_order_id_367fc77f ON public.trader_order USING btree (client_order_id);
CREATE INDEX trader_order_client_order_id_367fc77f_like ON public.trader_order USING btree (client_order_id varchar_pattern_ops);
CREATE INDEX trader_order_market_id_3e0678ac ON public.trader_order USING btree (market_id);
CREATE INDEX trader_order_placed_by_id_28faa213 ON public.trader_order USING btree (placed_by_id);
CREATE INDEX trader_order_placed_by_id_28faa213_like ON public.trader_order USING btree (placed_by_id varchar_pattern_ops);
CREATE INDEX trader_order_timestamp_idx ON public.trader_order USING btree ("timestamp" DESC);

-- Table Triggers

create trigger ts_insert_blocker before
insert
    on
    public.trader_order for each row execute function _timescaledb_internal.insert_blocker();
        '''),
        migrations.RunSQL('''
        -- public.trader_fill definition

-- Drop table

DROP TABLE public.trader_fill;

CREATE TABLE public.trader_fill (
	id bigserial NOT NULL,
	exchange_id varchar(32) NOT NULL,
	exchange_order_id varchar(32) NOT NULL,
	market_id int4 NOT NULL,
	"timestamp" timestamptz NOT NULL,
	price numeric(32, 16) NULL,
	volume numeric(32, 16) NOT NULL,
	is_sell bool NOT NULL,
	fee numeric(32, 16) NOT NULL,
	fee_asset_id int4 NOT NULL,
	account_id int8 NOT NULL,
	CONSTRAINT trader_fill_account_id_46409e97_fk_trader_account_id FOREIGN KEY (account_id) REFERENCES public.trader_account(id) DEFERRABLE INITIALLY DEFERRED
);
CREATE INDEX trader_fill_account_id_46409e97 ON public.trader_fill USING btree (account_id);
CREATE INDEX trader_fill_exchange_id_dcdb1594 ON public.trader_fill USING btree (exchange_id);
CREATE INDEX trader_fill_exchange_order_id_c1178787 ON public.trader_fill USING btree (exchange_order_id);
CREATE INDEX trader_fill_market_id_6e813bd0 ON public.trader_fill USING btree (market_id);
CREATE INDEX trader_fill_timestamp_idx ON public.trader_fill USING btree ("timestamp" DESC);

-- Table Triggers

create trigger ts_insert_blocker before
insert
    on
    public.trader_fill for each row execute function _timescaledb_internal.insert_blocker();
        '''),
    ]
