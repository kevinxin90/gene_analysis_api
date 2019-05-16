import json
from pathlib import Path
from tornado.ioloop import IOLoop

from .base import BaseHandler
from .environment import FunctionalSimilarity
from .utils import hashInput, check_job_status, write_result_to_file


class FunctionalSimilarityHandler(BaseHandler):
    """
    Find similar genes based on GO functional annotations using OntoBio Jaccard similarity

    Params
    ======
    DefaultDict grouped by semantic type
    """

    def callback_task(self, hash_input, input_curie_list, taxon, threshold):
        try:
            print('hash_input', hash_input, 'input_curie_list', input_curie_list, 'taxon', taxon, 'threshold', threshold)
            input_curie_set = [{"hit_id": _gene, "hit_symbol": None} for _gene in input_curie_list]
            mod1a_input_object_human = {
                "input": input_curie_set,
                "parameters": {
                    "taxon": taxon,
                    "threshold": threshold
                }
            }
            func_sim_human = FunctionalSimilarity()
            func_sim_human.load_input_object(mod1a_input_object_human)
            func_sim_human.load_gene_set()
            func_sim_human.load_associations()
            mod1a_results = func_sim_human.compute_similarity()
            write_result_to_file(hash_input, mod1a_results)
        except:
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

