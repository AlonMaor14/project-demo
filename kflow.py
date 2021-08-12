import mlrun
from kfp import dsl

funcs = {}
project = mlrun.projects.pipeline_context.project
iris_data = 'https://s3.wasabisys.com/iguazio/data/iris/iris.data.raw.csv'
default_pkg_class = "sklearn.linear_model.LogisticRegression"

@dsl.pipeline(
    name="Demo training pipeline",
    description="Shows how to use mlrun."
)
def kfpipeline(model_pkg_class=default_pkg_class):

    # run a local data prep function
    prep_data = funcs["prep-data"].as_step(name='prep_data',
                                           inputs={'source_url': project.get_artifact_uri("data")},
                                           outputs=["cleaned_data"])

    # train the model using a library (hub://) function and the generated data
    train = funcs["train"].as_step(name='train',
                                   inputs={'dataset': prep_data.outputs['cleaned_data']},
                                   params={'model_pkg_class': model_pkg_class,
                                           'label_column': project.get_param('label', 'label')},
                                   outputs=["model", "test_set"])

    # test the model using a library (hub://) function and the generated model
    test = funcs["test"].as_step(name="test",
                                 params={"label_column": "label"},
                                 inputs={"models_path": train.outputs['model'],
                                         "test_set": train.outputs['test_set']})
