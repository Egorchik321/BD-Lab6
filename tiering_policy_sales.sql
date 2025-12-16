
        -- Автоматический переход старых данных в холодное хранилище
        ALTER TABLE sales SET TBLPROPERTIES (
            "storage_handler" = "org.apache.hadoop.hive.ql.storage.ArchiveStorageHandler",
            "retention_days" = "365",
            "tiering_policy" = "{
                'hot': {'days': 7},
                'warm': {'days': 30},
                'cold': {'days': 365}
            }"
        );
        