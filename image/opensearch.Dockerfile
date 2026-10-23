FROM opensearchproject/opensearch:2.19.6
RUN /usr/share/opensearch/bin/opensearch-plugin install --batch ingest-attachment \
    && /usr/share/opensearch/bin/opensearch-plugin install --batch analysis-kuromoji \
    && /usr/share/opensearch/bin/opensearch-plugin install --batch repository-s3
