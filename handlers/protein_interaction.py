import json
from pathlib import Path
from tornado.ioloop import IOLoop
import pandas as pd

from .base import BaseHandler
from .environment import GeneInteractions
from .utils import hashInput, check_job_status, write_result_to_file


class ProteinInteractionHandler(BaseHandler):
    """
    Find similar genes based on Protein Interaction

    """

    def callback_task(self, hash_input, input_curie_list, taxon, threshold):
        try:
            input_curie_set = [{"hit_id": _gene, "hit_symbol": None} for _gene in input_curie_list]
            mod1E_input_object_human = {
                'input': input_curie_set,
                 'parameters': {
                    'taxon': 'human',
                    'threshold': None,
                },
            }
            interactions_human = GeneInteractions()
            interactions_human.load_input_object(mod1E_input_object_human)
            interactions_human.load_gene_set()
            mod1e_results = interactions_human.get_interactions()
            Mod1E_results_human = pd.DataFrame(mod1e_results)
            counts = Mod1E_results_human['hit_symbol'].value_counts().rename_axis('unique_values').to_frame('counts').reset_index()
            high_counts = counts[counts['counts'] > 12]['unique_values'].tolist()
            Mod1E_results_final = pd.DataFrame(Mod1E_results_human[Mod1E_results_human['hit_symbol'].isin(high_counts)])
            mod1e_results = Mod1E_results_final.to_dict('records')
            write_result_to_file(hash_input, mod1e_results)
        except Exception as e:
            print('Failed to upload to ftp: '+ str(e))
            write_result_to_file(hash_input, {})

    async def get(self):
        # get input parameters
        taxon = self.get_query_argument('taxon', 'human')
        threshold = float(self.get_query_argument('threshold', 0.75))
        input_curies = self.get_query_argument('input_gene_list')
        input_curie_list = input_curies.split(',')
        # convert input into hash
        hash_input = hashInput(taxon + str(threshold) + input_curies)
        """
        Check job status
        1) If hash file not exists, create one and set status to be "in processing"
        2) If has file exists:
            a) If file status is "in processing", return "in processing"
            b) If file status is "ready", return results
        """
        job_status, results = check_job_status(hash_input)
        print('job status', job_status)
        # return "in processing" if status is processing
        if job_status == "In processing":
            self.write(json.dumps({"status": "In processing!"}))
            self.finish()
        # start processing data if the job not exists yet
        elif job_status == "New job started":
            self.write(json.dumps({"status": "Your job has just started, please check back later!"}))
            self.finish()
            # gene functional similarity analysis
            res = await IOLoop.current().run_in_executor(None, self.callback_task, *(hash_input, input_curie_list, taxon, threshold))
        # write results to output if status is completed
        elif job_status == "Completed":
            self.write(json.dumps({'results': results}))
            self.finish()
        else:
            self.write(json.dumps({'info': job_status}))
            self.finish()

