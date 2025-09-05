const Result = ({ recipe, query, shoppingList, haveItems }) => {
    return (
        <div className="container">
            <div className="card">
                <div className="card-header d-flex justify-content-between align-items-center">
                    <h1 className="card-title mb-0">{recipe.title}</h1>
                    <a href="/home" className="btn btn-secondary">Generate Another</a>
                </div>
                <div className="card-body">
                    {recipe.description && <p className="lead">{recipe.description}</p>}

                    <div className="row">
                        <div className="col-md-5">
                            <h2>Ingredients</h2>
                            {haveItems && haveItems.length > 0 && (
                                <>
                                    <h4>You have:</h4>
                                    <ul className="list-group mb-3">
                                        {haveItems.map((item, index) => (
                                            <li key={index} className="list-group-item list-group-item-success">
                                                {item.ingredient} ({item.quantity})
                                            </li>
                                        ))}
                                    </ul>
                                </>
                            )}

                            {shoppingList && shoppingList.length > 0 && (
                                <>
                                    <h4>Shopping List:</h4>
                                    <ul className="list-group">
                                        {shoppingList.map((item, index) => (
                                            <li key={index} className="list-group-item list-group-item-warning">
                                                {item.ingredient} ({item.quantity})
                                            </li>
                                        ))}
                                    </ul>
                                </>
                            )}
                        </div>

                        <div className="col-md-7">
                            <h2>Instructions</h2>
                            <ol className="list-group list-group-numbered">
                                {recipe.steps.map((step, index) => (
                                    <li key={index} className="list-group-item">{step}</li>
                                ))}
                            </ol>
                        </div>
                    </div>
                </div>
                <div className="card-footer text-muted">
                    <p>Generated based on your query: "<em>{query}</em>"</p>
                </div>
            </div>
        </div>
    );
};
