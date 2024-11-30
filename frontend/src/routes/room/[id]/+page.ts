export async function load({ params }) {
    const { id } = params;
    console.log(id);

    return {
        props: {
            id
        }
    }
}