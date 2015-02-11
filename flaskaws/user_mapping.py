SETTINGS = {
    "index": {
        "analysis": {
            "analyzer": {
                "lowercase": {
                    "tokenizer": "keyword",
                    "filter": "lowercase"
                },
                "title_stemming": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "snowball"]
                },
                "autocomplete":{
                    "type":"custom",
                    "tokenizer":"standard",
                    "filter":[ "standard", "lowercase", "stop", "kstem", "ngram" ]
                },
            },
            "filter": {
                "ngram": {
                    "type": "nGram",
                    "min_gram": 2,
                    "max_gram": 8,
                },
                "snowball": {
                    "type": "snowball",
                    "language": "English"
                }
            },
        }
    }
}

USER = {
    "efid": {"type": "long",},
    "clients":{
        "properties":{
            "asid":{"type":"string", "index":"not_analyzed"},
            "id":{"type":"string", "index":"not_analyzed"},
        }
    },
    "first_name": {"type": "string",},
    "last_name": {"type": "string",},
    "location":{
        "properties":{
            "location":{"type": "string"},
            "city": {
                "type": "multi_field",
                "fields":{
                    "facet":{
                        "type":"string",
                        "index": "not_analyzed"
                    },
                    "suggest": {
                        "type": "string",
                        "analyzer": "autocomplete"
                    }
                }
            },
            "state": {
                "type": "multi_field",
                "fields":{
                    "facet":{
                        "type":"string",
                        "index": "not_analyzed"
                    },
                    "suggest": {
                        "type": "string",
                        "analyzer": "autocomplete"
                    }
                }
            },
        }
    },
    "locale":{
        "type": "multi_field",
        "fields": {
            "search": {
                "type": "string"
            },
            "facet": {
                "type": "string",
                "index": "not_analyzed",
            },
            "suggest": {
                "type": "string",
                "analyzer": "autocomplete"
            }
        }
    },
    "last_activity": {"type": "date",},
    "first_activity": {"type": "date",},
    "birthday": {"type": "date",},
    "gender": {"type": "string", "index": "not_analyzed",},
    "age":{"type": "integer",},
    "num_friends":{"type": "integer",},
    "num_posts":{"type": "integer",},
    "num_mine_liked":{"type": "integer",},
    "num_mine_commented":{"type": "integer",},
    "num_i_shared":{"type": "integer",},
    "num_stat_upd":{"type": "integer",},
    "num_people_interacted_with_my_posts":{"type": "integer"},
    "avg_time_between_activity":{"type": "integer"},
    "avg_people_interacted_with_my_posts":{"type": "integer"},
    "top_words":{
        "type": "multi_field",
        "fields": {
            "search": {
                "type": "string"
            },
            "facet": {
                "type": "string",
                "index": "not_analyzed",
            },
            "suggest": {
                "type": "string",
                "analyzer": "autocomplete"
            }
        }
    },
    "affiliations": {
        "properties":{
            "category": {"type": "string", "index": "not_analyzed"},
            "name": {
                "type": "multi_field",
                "fields": {
                    "search": {
                        "type": "string"
                    },
                    "facet": {
                        "type": "string",
                        "index": "not_analyzed",
                    },
                    "suggest": {
                        "type": "string",
                        "analyzer": "autocomplete"
                    }
                }
            }
        }
    },
    "likes": {
        "properties":{
            "category": {"type": "string", "index": "not_analyzed"},
            "name": {
                "type": "multi_field",
                "fields": {
                    "search": {
                        "type": "string"
                    },
                    "facet": {
                        "type": "string",
                        "index": "not_analyzed",
                    },
                    "suggest": {
                        "type": "string",
                        "analyzer": "autocomplete"
                    }
                }
            }
        }
    },
    "email": {
        "properties":{
            "email":{"type":"string"},
            "handle":{
                "type":"string"
            },
            "domain":{
                "type": "multi_field",
                "fields": {
                    "search": {
                        "type": "string"
                    },
                    "facet": {
                        "index": "not_analyzed",
                        "type": "string",
                    },
                    "suggest": {
                        "type": "string",
                        "analyzer": "autocomplete"
                    }
                }
            }
        }
    },
 }
