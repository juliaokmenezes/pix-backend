from django.test import TestCase, Client
from django.urls import reverse
from .models import Pix, PixStream
from .service import MAX_STREAMS, MULTIPART_LIMIT
from .service import criar_ou_validar_stream


class PixApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.ispb = "32074986"

    def test_cadastro_pix_post(self):
        url = reverse('cadastro_pix', args=[self.ispb, 5])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Pix.objects.filter(recebedor_ispb=self.ispb).count(), 5)
        self.assertJSONEqual(response.content, {"mensagem": "Pix Cadastrado com Sucesso"})

    def test_cadastro_pix_get_method_not_allowed(self):
        url = reverse('cadastro_pix', args=[self.ispb, 1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_recuperacao_mensagens_json(self):
        self.client.post(reverse('cadastro_pix', args=[self.ispb, 3]))
        url = reverse('pix_stream_start', args=[self.ispb])
        response = self.client.get(url, HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('mensagens', data)
        self.assertEqual(len(data['mensagens']), 1)  
        self.assertIn('Pull-Next', response)

    def test_recuperacao_mensagens_multipart(self):
        self.client.post(reverse('cadastro_pix', args=[self.ispb, 15]))
        url = reverse('pix_stream_start', args=[self.ispb])
        response = self.client.get(url, HTTP_ACCEPT='multipart/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('mensagens', data)
        self.assertLessEqual(len(data['mensagens']), MULTIPART_LIMIT)

    def test_recuperacao_mensagens_sem_mensagens(self):
        iterationId, _ = criar_ou_validar_stream("32074986")
        response = self.client.get(f"/api/pix/32074986/stream/{iterationId}", HTTP_ACCEPT="application/json")
        self.assertIn(response.status_code, [200, 204])
        if response.status_code == 200:
            self.assertJSONEqual(response.content, {"mensagens": []})


    def test_iterationId_continuation_and_invalid(self):
        self.client.post(reverse('cadastro_pix', args=[self.ispb, 2]))
        start_response = self.client.get(reverse('pix_stream_start', args=[self.ispb]))
        iterationId = start_response['Pull-Next'].split('/')[-1]

        cont_url = reverse('pix_stream_continuation', args=[self.ispb, iterationId])
        response = self.client.get(cont_url)
        self.assertEqual(response.status_code, 200)

        invalid_url = reverse('pix_stream_continuation', args=[self.ispb, 'invalidid'])
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)

    def test_stream_delete_success_and_failures(self):
        self.client.post(reverse('cadastro_pix', args=[self.ispb, 2]))
        start_response = self.client.get(reverse('pix_stream_start', args=[self.ispb]))
        iterationId = start_response['Pull-Next'].split('/')[-1]

        delete_url = reverse('pix_stream_delete', args=[self.ispb, iterationId])
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, 404)

        response = self.client.get(delete_url)
        self.assertEqual(response.status_code, 405)

    def test_max_streams_limit(self):
        iteration_ids = []
        for _ in range(MAX_STREAMS):
            resp = self.client.get(reverse('pix_stream_start', args=[self.ispb]))
            iteration_ids.append(resp['Pull-Next'].split('/')[-1])

        resp = self.client.get(reverse('pix_stream_start', args=[self.ispb]))
        self.assertEqual(resp.status_code, 429)

    def test_multiples_messages_only_once(self):
        total_msgs = 12
        self.client.post(reverse('cadastro_pix', args=[self.ispb, total_msgs]))
        url = reverse('pix_stream_start', args=[self.ispb])
        
        todas_mensagens_ids = set()
        while True:
            response = self.client.get(url, HTTP_ACCEPT='multipart/json')
            if response.status_code == 204:
                break
            data = response.json()
            for msg in data['mensagens']:
                self.assertNotIn(msg['endToEndId'], todas_mensagens_ids)
                todas_mensagens_ids.add(msg['endToEndId'])
        
        self.assertEqual(len(todas_mensagens_ids), total_msgs)
        
        from .models import Pix
        self.assertFalse(Pix.objects.filter(recebedor_ispb=self.ispb, dado_visualizado=False).exists())
