const { useState, useEffect } = React;

const ThemeToggle = () => {
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    if (localStorage.getItem('theme') === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      document.documentElement.classList.add('dark');
      setIsDarkMode(true);
    } else {
      document.documentElement.classList.remove('dark');
      setIsDarkMode(false);
    }
  }, []);

  const toggleTheme = () => {
    if (isDarkMode) {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    } else {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    }
    setIsDarkMode(!isDarkMode);
  };

  return (
    <button onClick={toggleTheme} className="absolute top-4 right-4 p-2 rounded-full bg-gray-200 dark:bg-gray-800 text-gray-800 dark:text-gray-200">
      {isDarkMode ? 'Light' : 'Dark'}
    </button>
  );
};

const Result = ({ recipe, shopping_list, have_items }) => {
  // In a real app, these props would be passed from the server
  const mockRecipe = {
    title: "Delicious Chicken Curry",
    description: "A rich and aromatic chicken curry that's easy to make.",
    servings: "4",
    prep_time: "15 minutes",
    cook_time: "30 minutes",
    ingredients: [
      { name: "Chicken Breast", quantity: "2", unit: "lbs" },
      { name: "Onion", quantity: "1", unit: "" },
      { name: "Garlic", quantity: "3", unit: "cloves" },
      { name: "Ginger", quantity: "1", unit: "inch" },
      { name: "Tomatoes", quantity: "14.5", unit: "oz" },
      { name: "Coconut Milk", quantity: "13.5", unit: "oz" },
      { name: "Curry Powder", quantity: "2", unit: "tbsp" },
    ],
    steps: [
      "Cut chicken into bite-sized pieces.",
      "Chop onion, garlic, and ginger.",
      "Sauté onion, garlic, and ginger in a large pot.",
      "Add chicken and cook until browned.",
      "Stir in curry powder and cook for 1 minute.",
      "Add tomatoes and coconut milk. Bring to a simmer.",
      "Reduce heat and cook for 15-20 minutes, or until chicken is cooked through.",
    ],
  };

  const mockShoppingList = [
      { name: "Chicken Breast", quantity: "2", unit: "lbs" },
      { name: "Coconut Milk", quantity: "13.5", unit: "oz" },
  ]

  const mockHaveItems = [
    { name: "Onion", quantity: "1", unit: "" },
    { name: "Garlic", quantity: "3", unit: "cloves" },
    { name: "Ginger", quantity: "1", unit: "inch" },
    { name: "Tomatoes", quantity: "14.5", unit: "oz" },
    { name: "Curry Powder", quantity: "2", unit: "tbsp" },
  ]

  const finalRecipe = recipe || mockRecipe;
  const finalShoppingList = shopping_list || mockShoppingList;
  const finalHaveItems = have_items || mockHaveItems;

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
      <ThemeToggle />
      <nav className="bg-white dark:bg-gray-800 shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex-shrink-0">
              <a href="/home" className="text-xl font-bold">Recipe Generator</a>
            </div>
            <div className="flex items-center">
              <a href="/logout" className="text-sm font-medium text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-gray-100">Logout</a>
            </div>
          </div>
        </div>
      </nav>
      <main className="max-w-4xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
            <h2 className="text-3xl font-extrabold sm:text-4xl">
                {finalRecipe.title}
            </h2>
            <p className="mt-4 text-lg text-gray-500 dark:text-gray-400">
                {finalRecipe.description}
            </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="md:col-span-2">
                <h3 className="text-2xl font-bold mb-4">Ingredients</h3>
                <ul className="list-disc list-inside space-y-2">
                    {finalRecipe.ingredients.map((ing, i) => (
                        <li key={i}>{ing.quantity} {ing.unit} {ing.name}</li>
                    ))}
                </ul>

                <h3 className="text-2xl font-bold mt-8 mb-4">Instructions</h3>
                <ol className="list-decimal list-inside space-y-4">
                    {finalRecipe.steps.map((step, i) => (
                        <li key={i}>{step}</li>
                    ))}
                </ol>
            </div>
            <div>
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                    <h3 className="text-xl font-bold mb-4">Shopping List</h3>
                    <ul className="space-y-2">
                        {finalShoppingList.map((item, i) => (
                            <li key={i} className="flex items-center">
                                <input type="checkbox" className="h-4 w-4 text-primary-600 border-gray-300 rounded" />
                                <span className="ml-2">{item.quantity} {item.unit} {item.name}</span>
                            </li>
                        ))}
                    </ul>
                    <h3 className="text-xl font-bold mt-6 mb-4">You Have</h3>
                    <ul className="space-y-2">
                        {finalHaveItems.map((item, i) => (
                            <li key={i} className="flex items-center text-gray-500 dark:text-gray-400 line-through">
                                <input type="checkbox" checked disabled className="h-4 w-4 text-primary-600 border-gray-300 rounded" />
                                <span className="ml-2">{item.quantity} {item.unit} {item.name}</span>
                            </li>
                        ))}
                    </ul>
                </div>
            </div>
        </div>
        <div className="mt-12 text-center">
            <a href="/home" className="text-primary-600 hover:text-primary-500">
                &larr; Back to Home
            </a>
        </div>
      </main>
    </div>
  );
};

export default Result;
