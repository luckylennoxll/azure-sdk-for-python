# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import functools
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.exceptions import HttpResponseError
from azure.ai.formrecognizer._generated.v2023_02_28_preview.models import AnalyzeResultOperation
from azure.ai.formrecognizer.aio import DocumentAnalysisClient
from azure.ai.formrecognizer import AnalysisFeature, AnalyzeResult
from preparers import FormRecognizerPreparer
from asynctestcase import AsyncFormRecognizerTest
from preparers import GlobalClientPreparer as _GlobalClientPreparer
from conftest import skip_flaky_test


DocumentAnalysisClientPreparer = functools.partial(_GlobalClientPreparer, DocumentAnalysisClient)


class TestDACAnalyzeLayoutAsync(AsyncFormRecognizerTest):

    @skip_flaky_test
    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy_async
    async def test_layout_incorrect_feature_format(self, client):
        with open(self.invoice_pdf, "rb") as fd:
            document = fd.read()
        async with client:
            with pytest.raises(HttpResponseError):
                poller = await client.begin_analyze_document(
                    "prebuilt-layout",
                    document,
                    features=AnalysisFeature.OCR_FONT
                )

    @skip_flaky_test
    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy_async
    async def test_layout_stream_transform_pdf(self, client):
        with open(self.invoice_pdf, "rb") as fd:
            document = fd.read()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeResultOperation, raw_response)
            extracted_layout = AnalyzeResult._from_generated(analyze_result.analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_layout)

        async with client:
            poller = await client.begin_analyze_document(
                "prebuilt-layout",
                document,
                features=[AnalysisFeature.OCR_FONT],
                cls=callback
            )
            result = await poller.result()
        raw_analyze_result = responses[0].analyze_result
        returned_model = responses[1]

        # Check AnalyzeResult
        assert returned_model.model_id == raw_analyze_result.model_id
        assert returned_model.api_version == raw_analyze_result.api_version
        assert returned_model.content == raw_analyze_result.content
        
        self.assertDocumentPagesTransformCorrect(returned_model.pages, raw_analyze_result.pages)
        self.assertDocumentTransformCorrect(returned_model.documents, raw_analyze_result.documents)
        self.assertDocumentTablesTransformCorrect(returned_model.tables, raw_analyze_result.tables)
        self.assertDocumentKeyValuePairsTransformCorrect(returned_model.key_value_pairs, raw_analyze_result.key_value_pairs)
        self.assertDocumentStylesTransformCorrect(returned_model.styles, raw_analyze_result.styles)

        # check page range
        assert len(raw_analyze_result.pages) == len(returned_model.pages)

    @skip_flaky_test
    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy_async
    async def test_layout_stream_transform_jpg(self, client):
        with open(self.form_jpg, "rb") as fd:
            document = fd.read()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeResultOperation, raw_response)
            extracted_layout = AnalyzeResult._from_generated(analyze_result.analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_layout)

        async with client:
            poller = await client.begin_analyze_document("prebuilt-layout", document, cls=callback)
            result = await poller.result()
        raw_analyze_result = responses[0].analyze_result
        returned_model = responses[1]

        # Check AnalyzeResult
        assert returned_model.model_id == raw_analyze_result.model_id
        assert returned_model.api_version == raw_analyze_result.api_version
        assert returned_model.content == raw_analyze_result.content
        
        self.assertDocumentPagesTransformCorrect(returned_model.pages, raw_analyze_result.pages)
        self.assertDocumentTransformCorrect(returned_model.documents, raw_analyze_result.documents)
        self.assertDocumentTablesTransformCorrect(returned_model.tables, raw_analyze_result.tables)
        self.assertDocumentKeyValuePairsTransformCorrect(returned_model.key_value_pairs, raw_analyze_result.key_value_pairs)
        self.assertDocumentStylesTransformCorrect(returned_model.styles, raw_analyze_result.styles)

        # check page range
        assert len(raw_analyze_result.pages) == len(returned_model.pages)

    @skip_flaky_test
    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy_async
    async def test_layout_multipage_transform(self, client):
        with open(self.multipage_invoice_pdf, "rb") as fd:
            document = fd.read()

        responses = []

        def callback(raw_response, _, headers):
            analyze_result = client._deserialize(AnalyzeResultOperation, raw_response)
            extracted_layout = AnalyzeResult._from_generated(analyze_result.analyze_result)
            responses.append(analyze_result)
            responses.append(extracted_layout)

        async with client:
            poller = await client.begin_analyze_document("prebuilt-layout", document, cls=callback)
            result = await poller.result()
        raw_analyze_result = responses[0].analyze_result
        returned_model = responses[1]

        # Check AnalyzeResult
        assert returned_model.model_id == raw_analyze_result.model_id
        assert returned_model.api_version == raw_analyze_result.api_version
        assert returned_model.content == raw_analyze_result.content
        
        self.assertDocumentPagesTransformCorrect(returned_model.pages, raw_analyze_result.pages)
        self.assertDocumentTransformCorrect(returned_model.documents, raw_analyze_result.documents)
        self.assertDocumentTablesTransformCorrect(returned_model.tables, raw_analyze_result.tables)
        self.assertDocumentKeyValuePairsTransformCorrect(returned_model.key_value_pairs, raw_analyze_result.key_value_pairs)
        self.assertDocumentStylesTransformCorrect(returned_model.styles, raw_analyze_result.styles)

        # check page range
        assert len(raw_analyze_result.pages) == len(returned_model.pages)

    @pytest.mark.live_test_only
    @skip_flaky_test
    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy_async
    async def test_layout_multipage_table_span_pdf(self, client):
        with open(self.multipage_table_pdf, "rb") as fd:
            my_file = fd.read()
        async with client:
            poller = await client.begin_analyze_document("prebuilt-layout", my_file)
            layout = await poller.result()
        assert len(layout.tables) == 3
        assert layout.tables[0].row_count == 30
        assert layout.tables[0].column_count == 5
        assert layout.tables[1].row_count == 6
        assert layout.tables[1].column_count == 5
        assert layout.tables[2].row_count == 24
        assert layout.tables[2].column_count == 5

    @pytest.mark.live_test_only
    @skip_flaky_test
    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy_async
    async def test_layout_url_annotations(self, client):
        async with client:
            poller = await client.begin_analyze_document_from_url("prebuilt-layout", self.annotations_url_jpg)
            layout = await poller.result()
        assert len(layout.pages) > 0
        assert len(layout.pages[0].annotations) > 0
        assert layout.pages[0].annotations[0].kind == "check"
        assert layout.pages[0].annotations[0].polygon
        assert layout.pages[0].annotations[0].confidence > 0.5

    @pytest.mark.live_test_only
    @skip_flaky_test
    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy_async
    async def test_layout_url_barcodes(self, client):
        async with client:
            poller = await client.begin_analyze_document_from_url("prebuilt-layout", self.barcode_url_tif)
            layout = await poller.result()
        assert len(layout.pages) > 0
        assert len(layout.pages[0].barcodes) == 2
        assert layout.pages[0].barcodes[0].kind == "Code39"
        assert layout.pages[0].barcodes[0].polygon
        assert layout.pages[0].barcodes[0].confidence > 0.8

    @skip_flaky_test
    @FormRecognizerPreparer()
    @DocumentAnalysisClientPreparer()
    @recorded_by_proxy_async
    async def test_layout_specify_pages(self, client):
        with open(self.multipage_invoice_pdf, "rb") as fd:
            document = fd.read()

        async with client:
            poller = await client.begin_analyze_document("prebuilt-layout", document, pages="1")
            result = await poller.result()
            assert len(result.pages) == 1

            poller = await client.begin_analyze_document("prebuilt-layout", document, pages="1, 3")
            result = await poller.result()
            assert len(result.pages) == 2

            poller = await client.begin_analyze_document("prebuilt-layout", document, pages="1-2")
            result = await poller.result()
            assert len(result.pages) == 2

            poller = await client.begin_analyze_document("prebuilt-layout", document, pages="1-2, 3")
            result = await poller.result()
            assert len(result.pages) == 3
